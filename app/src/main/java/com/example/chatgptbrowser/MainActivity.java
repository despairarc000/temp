package com.example.chatgptbrowser;
import android.app.*;
import android.content.*;
import android.net.Uri;
import android.os.*;
import android.webkit.*;
import android.widget.Toast;
public class MainActivity extends Activity {
 WebView web; ValueCallback<Uri[]> upload; static final int PICK=42;
 @Override public void onCreate(Bundle b){super.onCreate(b); web=new WebView(this);setContentView(web);
 WebSettings s=web.getSettings();s.setJavaScriptEnabled(true);s.setDomStorageEnabled(true);s.setAllowFileAccess(false);s.setAllowContentAccess(true);s.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
 CookieManager.getInstance().setAcceptCookie(true);CookieManager.getInstance().setAcceptThirdPartyCookies(web,true);
 web.setWebViewClient(new WebViewClient(){@Override public boolean shouldOverrideUrlLoading(WebView v,WebResourceRequest r){Uri u=r.getUrl();String h=u.getHost();if("https".equalsIgnoreCase(u.getScheme())&&h!=null&&(h.equals("chatgpt.com")||h.endsWith(".chatgpt.com")||h.equals("openai.com")||h.endsWith(".openai.com")))return false;external(u);return true;}});
 web.setWebChromeClient(new WebChromeClient(){@Override public boolean onShowFileChooser(WebView v,ValueCallback<Uri[]> cb,FileChooserParams p){if(upload!=null)upload.onReceiveValue(null);upload=cb;try{startActivityForResult(p.createIntent(),PICK);return true;}catch(Exception e){upload=null;return false;}}});
 web.setDownloadListener((url,ua,disp,mime,len)->{try{Uri u=Uri.parse(url);if(!"https".equalsIgnoreCase(u.getScheme())){external(u);return;}DownloadManager.Request req=new DownloadManager.Request(u);req.setMimeType(mime);req.addRequestHeader("User-Agent",ua);String c=CookieManager.getInstance().getCookie(url);if(c!=null)req.addRequestHeader("Cookie",c);req.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED);req.setDestinationInExternalFilesDir(this,Environment.DIRECTORY_DOWNLOADS,"chatgpt-"+System.currentTimeMillis());((DownloadManager)getSystemService(DOWNLOAD_SERVICE)).enqueue(req);Toast.makeText(this,"Downloading",Toast.LENGTH_SHORT).show();}catch(Exception e){external(Uri.parse(url));}});
 web.loadUrl("https://chatgpt.com/");}
 void external(Uri u){try{startActivity(new Intent(Intent.ACTION_VIEW,u));}catch(Exception e){Toast.makeText(this,"Cannot open link",Toast.LENGTH_SHORT).show();}}
 @Override protected void onActivityResult(int r,int result,Intent data){super.onActivityResult(r,result,data);if(r==PICK&&upload!=null){upload.onReceiveValue(WebChromeClient.FileChooserParams.parseResult(result,data));upload=null;}}
 @Override public void onBackPressed(){if(web!=null&&web.canGoBack())web.goBack();else super.onBackPressed();}
 @Override protected void onDestroy(){if(upload!=null)upload.onReceiveValue(null);if(web!=null)web.destroy();super.onDestroy();}
}
