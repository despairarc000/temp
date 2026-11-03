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
    }
    if not all(checks.values()):raise ValueError('account chain changed: '+','.join(k for k,v in checks.items() if not v))
    return checks
