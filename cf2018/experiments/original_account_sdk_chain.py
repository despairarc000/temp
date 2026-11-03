"""Hash-pinned read-only original APK account-chain audit. No network or values.

Only method references/fixed booleans leave this analysis. No manifest keys,
provider credentials, saved account data or original code are exported.
"""
import hashlib,io
from pathlib import Path
from zipfile import ZipFile
APK_SHA='33045335685284385866e8b0e2df55285009399c285294c2f428b451ee00d3d9'

def audit(path):
    raw=Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=APK_SHA:raise ValueError('exact original APK required')
    from loguru import logger
    logger.disable('androguard')
    from androguard.core.dex import DEX
    with ZipFile(io.BytesIO(raw)) as z:dex=DEX(z.read('classes.dex'))
    root='Lcom/tencent/imsdk/android/'
    def methods(cls,name):
        c=dex.get_class(root+cls+';')
        if c is None:raise ValueError('original class missing')
        return [m for m in c.get_methods() if m.get_name()==name]
    def refs(cls,name):
        values=[]
        for method in methods(cls,name):
            for pc,ins in method.get_instructions_idx():
                if ins.get_name().startswith('invoke-'):
                    values.extend(o[-1] for o in ins.get_operands() if len(o)>=3 and isinstance(o[-1],str))
        return values
    def has(cls,name,target):return any(target in s for s in refs(cls,name))
    strings=[i.get_operands()[-1][-1] for m in methods('base/login/IMSDKLoginBase','getUrl') for i in m.get_instructions() if i.get_name().startswith('const-string')]
    error=methods('tools/net/IMSDKHttpClient$2','onErrorResponse')
    if len(error)!=1:raise ValueError('original error callback changed')
    ins=dict(error[0].get_instructions_idx())
    handlers=methods('base/login/IMSDKLoginBase','handleServerData')
    if len(handlers)!=1:raise ValueError('original server handler changed')
    gate=dict(handlers[0].get_instructions_idx())
    https_methods=methods('base/IMSDKManagerBase','enableHttps')
    https_ops=list(https_methods[0].get_instructions()) if len(https_methods)==1 else []
    def field_annotations(cls,field_name):
        c=dex.get_class(root+cls+';');directory=dex.CM.get_annotations_directory_item(c.get_annotations_off())
        out=[]
        for f in directory.get_field_annotations():
            if dex.CM.get_field(f.get_field_idx())[-1]!=field_name:continue
            for off in dex.CM.get_annotation_set_item(f.get_annotations_off()).get_annotation_off_item():
                ann=off.get_annotation_item().get_annotation()
                if not dex.CM.get_type(ann.get_type_idx()).endswith('/JsonProp;'):continue
                out.extend(e.get_value().get_value() for e in ann.get_elements() if dex.CM.get_string(e.get_name_idx())=='value')
        return out
    checks={
        'google_starts_android_provider':has('login/google/GoogleLogin','login2Channel','->connectGoogleApiClient()'),
        'google_success_notifies_sdk':has('login/google/GoogleLogin$GoogleAuthConnectListener','handleConnectSuccess','->onNotify(Ljava/util/Map;)'),
        'provider_notify_starts_account_server':has('base/login/IMSDKLoginBase$2','onNotify','->connectIMSDK('),
        'provider_error_uses_separate_result_path':has('base/login/IMSDKLoginBase$2','onResult','->access$000('),
        'separate_result_path_returns_error':has('base/login/IMSDKLoginBase','access$000','->returnLRByError('),
        'account_url_uses_https_literal':'https' in [s.lower() for s in strings],
        'account_url_has_its_own_config':'IMSDK_SERVER_SDKAPI' in strings and 'IMSDK_SERVER_SDKAPI_VERSION' in strings,
        'server_result_parser_exists':has('base/login/IMSDKLoginBase','handleServerData','IMSDKLoginResult;-><init>(Ljava/lang/String;)'),
        'server_result_storage_exists':has('base/login/IMSDKLoginBase','handleServerData','->saveLoginData('),
        'guest_also_notifies_account_sdk':has('base/login/GuestLogin','login2Channel','->onNotify(Ljava/lang/Object;)'),
        'http_error_callback_sets_primary_four':ins[0x8e].get_name()=='const/4' and ins[0x8e].get_operands()==[(0,2),(1,4)] and ins[0xf2].get_name()=='invoke-direct',
        'http_client_uses_volley':has('tools/net/IMSDKHttpClient','post','->executeVolley('),
        'standard_queue_uses_hurlstack':has('tools/net/volley/toolbox/Volley','newRequestQueue','HurlStack;-><init>()'),
        'backend_status_maps_to_code':field_annotations('api/IMSDKResult','thirdRetCode')==['code'],
        'sdk_primary_is_separate':field_annotations('api/IMSDKResult','imsdkRetCode')==['imsdkRetCode'],
        'internal_identity_maps_to_iopenid':field_annotations('api/login/IMSDKLoginResult','openId')==['iOpenid'],
        'internal_token_maps_to_sinnertoken':field_annotations('api/login/IMSDKLoginResult','innerToken')==['sInnerToken'],
        'backend_success_comparator_is_one':gate[4].get_name()=='const/4' and gate[4].get_operands()==[(0,7),(1,1)] and gate[0x68].get_name()=='if-ne' and gate[0x68].get_operands()[:2]==[(0,5),(0,7)],
        'backend_branch_reads_third_status':gate[0x64].get_name()=='iget' and '->thirdRetCode I' in gate[0x64].get_operands()[-1][-1],
        'success_primary_set_after_gate':gate[0x6c].get_name()=='const/4' and gate[0x6c].get_operands()==[(0,5),(1,1)] and '->imsdkRetCode I' in gate[0x6e].get_operands()[-1][-1],
        'default_https_enabled':len(https_ops)==2 and https_ops[0].get_name()=='const/4' and https_ops[0].get_operands()==[(0,0),(1,1)] and https_ops[1].get_name()=='return',
        'config_url_consults_https_default':has('base/config/IMSDKConfigManager','getUrl','->enableHttps()'),
        'json_reflection_uses_optional_values_and_defaults':has('tools/json/JsonSerializable','fillWithJSON','JSONObject;->opt(') and has('tools/json/JsonSerializable','fillWithJSON','->getDefaultValue(') and has('tools/json/JsonSerializable','fillWithJSON','reflect/Field;->set('),
        'configuration_update_api_calls_user_database':has('api/config/IMSDKConfig','updateConfigs','->updateUserDB('),
    }
    if not all(checks.values()):raise ValueError('account chain changed: '+','.join(k for k,v in checks.items() if not v))
    return checks
