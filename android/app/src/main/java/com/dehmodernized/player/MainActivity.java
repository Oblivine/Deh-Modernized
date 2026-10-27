package com.dehmodernized.player;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.pm.ResolveInfo;
import android.provider.Settings;
import java.util.List;
import java.util.Collections;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import android.content.*;
import android.database.Cursor;
import android.media.AudioManager;
import android.media.MediaPlayer;
import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.provider.OpenableColumns;
import android.view.InputDevice;
import android.view.KeyEvent;
import android.view.MotionEvent;
import android.view.View;
import android.webkit.JavascriptInterface;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;
import androidx.webkit.WebViewAssetLoader;
import java.util.ArrayList;
import org.json.JSONArray;
import org.json.JSONObject;

public final class MainActivity extends Activity {
    private static final int PICK_AUDIO=201;
    private static final String PAGE="https://appassets.androidplatform.net/assets/www/index.html";
    private WebView web;
    private AudioManager audio;
    private MediaPlayer player;
    private final Handler handler=new Handler(Looper.getMainLooper());
    private final ArrayList<Uri> songs=new ArrayList<>();
    private int index=0;
    private int generation=0;
    private boolean ready=false, preparing=false, playWhenReady=false, pageReady=false, startAfterPick=false;
    private String state="stopped", message="", cachedTitle="Audio file", cachedTitleUri="";
    private final ExecutorService fileTasks=Executors.newSingleThreadExecutor();
    private android.content.SharedPreferences prefs;
    private final AudioManager.OnAudioFocusChangeListener focus=change->{
        if(change==AudioManager.AUDIOFOCUS_LOSS || change==AudioManager.AUDIOFOCUS_LOSS_TRANSIENT || change==AudioManager.AUDIOFOCUS_LOSS_TRANSIENT_CAN_DUCK){
            if(player!=null && ready && player.isPlaying()){player.pause();state="paused";sendState();}
        }
    };
    private final Runnable ticker=new Runnable(){public void run(){if(pageReady)sendState();handler.postDelayed(this,1000);}};

    @Override public void onCreate(Bundle saved){
        super.onCreate(saved);
        prefs=getSharedPreferences("deh-android",MODE_PRIVATE);
        audio=(AudioManager)getSystemService(AUDIO_SERVICE);
        restoreSongs();
        try{web=new WebView(this);}catch(RuntimeException ex){
            new AlertDialog.Builder(this).setTitle("Android WebView unavailable").setMessage("This unit needs a working Android System WebView to run DEH Modernized. Open Android settings to repair or update it.").setPositiveButton("Settings",(d,w)->{try{startActivity(new Intent(Settings.ACTION_SETTINGS));}catch(Exception ignored){}}).setNegativeButton("Close",(d,w)->finish()).show();return;
        }
        WebSettings settings=web.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(false);
        settings.setAllowContentAccess(false);
        settings.setAllowFileAccessFromFileURLs(false);
        settings.setAllowUniversalAccessFromFileURLs(false);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        settings.setMediaPlaybackRequiresUserGesture(true);
        WebViewAssetLoader loader=new WebViewAssetLoader.Builder().addPathHandler("/assets/",new WebViewAssetLoader.AssetsPathHandler(this)).build();
        web.setWebViewClient(new WebViewClient(){
            @Override public WebResourceResponse shouldInterceptRequest(WebView v,WebResourceRequest request){return loader.shouldInterceptRequest(request.getUrl());}
            @Override public boolean shouldOverrideUrlLoading(WebView v,WebResourceRequest request){return !"appassets.androidplatform.net".equals(request.getUrl().getHost());}
            @Override public void onPageFinished(WebView v,String url){if(PAGE.equals(url)){pageReady=true;sendState();v.evaluateJavascript("(window.CSS&&CSS.supports('width','1cqw')&&CSS.supports('height','100dvh'))?'ok':'old'",result->{if("\"old\"".equals(result)&&!isFinishing())new AlertDialog.Builder(MainActivity.this).setTitle("Update Android WebView").setMessage("This unit's WebView is too old for the player layout. Update Android System WebView or Chrome, then reopen the app.").setPositiveButton("Settings",(d,w)->{try{startActivity(new Intent(Settings.ACTION_SETTINGS));}catch(Exception ignored){}}).setNegativeButton("Continue",null).show();});}}
        });
        web.addJavascriptInterface(new Bridge(),"DEHNative");
        web.setFocusable(true);
        web.setFocusableInTouchMode(true);
        setContentView(web);
        web.loadUrl(PAGE);
        immersive();
        handler.post(ticker);
    }
    private void immersive(){getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_FULLSCREEN|View.SYSTEM_UI_FLAG_HIDE_NAVIGATION|View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY|View.SYSTEM_UI_FLAG_LAYOUT_STABLE|View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION|View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN);}
    @Override public void onWindowFocusChanged(boolean hasFocus){super.onWindowFocusChanged(hasFocus);if(hasFocus)immersive();}
    @Override protected void onResume(){super.onResume();if(web!=null)web.onResume();}
    @Override protected void onPause(){if(web!=null)web.onPause();super.onPause();}
    @Override protected void onDestroy(){generation++;handler.removeCallbacksAndMessages(null);fileTasks.shutdownNow();releasePlayer();audio.abandonAudioFocus(focus);if(web!=null){web.removeJavascriptInterface("DEHNative");web.destroy();web=null;}super.onDestroy();}

    private void navigate(String action){if(web!=null)web.evaluateJavascript("window.DEHNavigate&&window.DEHNavigate("+JSONObject.quote(action)+")",null);}
    @Override public boolean dispatchKeyEvent(KeyEvent event){
        int code=event.getKeyCode(); boolean down=event.getAction()==KeyEvent.ACTION_DOWN;
        boolean useVolume=prefs.getBoolean("volume_nav",false);
        String action=null;
        if(code==KeyEvent.KEYCODE_DPAD_LEFT||code==KeyEvent.KEYCODE_DPAD_UP||code==KeyEvent.KEYCODE_NAVIGATE_PREVIOUS)action="previous";
        else if(code==KeyEvent.KEYCODE_DPAD_RIGHT||code==KeyEvent.KEYCODE_DPAD_DOWN||code==KeyEvent.KEYCODE_NAVIGATE_NEXT)action="next";
        else if(code==KeyEvent.KEYCODE_DPAD_CENTER||code==KeyEvent.KEYCODE_ENTER||code==KeyEvent.KEYCODE_NUMPAD_ENTER)action="select";
        else if(useVolume&&code==KeyEvent.KEYCODE_VOLUME_DOWN)action="previous";
        else if(useVolume&&code==KeyEvent.KEYCODE_VOLUME_UP)action="next";
        else if(useVolume&&(code==KeyEvent.KEYCODE_VOLUME_MUTE||code==KeyEvent.KEYCODE_MUTE))action="select";
        if(down)recordInput("Key "+KeyEvent.keyCodeToString(code));
        if(action!=null){if(down&&(!"select".equals(action)||event.getRepeatCount()==0))navigate(action);return true;}
        return super.dispatchKeyEvent(event);
    }
    @Override public boolean dispatchGenericMotionEvent(MotionEvent event){
        if(event.getAction()==MotionEvent.ACTION_SCROLL&&event.isFromSource(InputDevice.SOURCE_ROTARY_ENCODER)){
            float delta=event.getAxisValue(MotionEvent.AXIS_SCROLL);
            if(delta!=0){recordInput("Rotary scroll "+delta);boolean reverse=prefs.getBoolean("reverse_dial",false);String direction=(delta>0)^reverse?"next":"previous";int count=Math.max(1,Math.min(10,Math.round(Math.abs(delta))));for(int i=0;i<count;i++)navigate(direction);return true;}
        }
        return super.dispatchGenericMotionEvent(event);
    }
    @Override public void onBackPressed(){
        if(web==null){super.onBackPressed();return;}
        web.evaluateJavascript("window.DEHBack?window.DEHBack():false",result->{if("false".equals(result))finish();});
    }
    private void recordInput(String text){prefs.edit().putString("last_input",text).apply();if(web!=null&&pageReady)web.evaluateJavascript("window.DEHInput&&window.DEHInput("+JSONObject.quote(text)+")",null);}

    private final class Bridge {
        @JavascriptInterface public void chooseMusic(){runOnUiThread(()->{startAfterPick=false;pickMusic();});}
        @JavascriptInterface public void playback(String command){runOnUiThread(()->perform(command));}
        @JavascriptInterface public void openApps(){runOnUiThread(()->showApps());}
        @JavascriptInterface public void homeSettings(){runOnUiThread(()->{try{startActivity(new Intent(Settings.ACTION_HOME_SETTINGS));}catch(Exception ex){Toast.makeText(MainActivity.this,"Home app settings are unavailable on this unit.",Toast.LENGTH_LONG).show();}});}
        @JavascriptInterface public void volumePanel(){runOnUiThread(()->audio.adjustStreamVolume(AudioManager.STREAM_MUSIC,AudioManager.ADJUST_SAME,AudioManager.FLAG_SHOW_UI));}
        @JavascriptInterface public void showMessage(String text){runOnUiThread(()->Toast.makeText(MainActivity.this,text,Toast.LENGTH_SHORT).show());}
        @JavascriptInterface public String options(){JSONObject j=new JSONObject();try{j.put("volumeNav",prefs.getBoolean("volume_nav",false));j.put("reverseDial",prefs.getBoolean("reverse_dial",false));j.put("lastInput",prefs.getString("last_input","No input received yet"));}catch(Exception ignored){}return j.toString();}
        @JavascriptInterface public void setOption(String key,boolean value){if("volumeNav".equals(key))prefs.edit().putBoolean("volume_nav",value).apply();else if("reverseDial".equals(key))prefs.edit().putBoolean("reverse_dial",value).apply();}
    }
    private void showApps(){
        Intent query=new Intent(Intent.ACTION_MAIN);query.addCategory(Intent.CATEGORY_LAUNCHER);
        List<ResolveInfo> apps=getPackageManager().queryIntentActivities(query,0);
        Collections.sort(apps,new ResolveInfo.DisplayNameComparator(getPackageManager()));
        ArrayList<ResolveInfo> visible=new ArrayList<>();ArrayList<String> names=new ArrayList<>();
        for(ResolveInfo info:apps){if(!getPackageName().equals(info.activityInfo.packageName)){visible.add(info);names.add(info.loadLabel(getPackageManager()).toString());}}
        if(visible.isEmpty()){Toast.makeText(this,"No other launcher apps are visible on this unit.",Toast.LENGTH_SHORT).show();return;}
        new AlertDialog.Builder(this).setTitle("Android apps").setItems(names.toArray(new String[0]),(dialog,which)->{
            ResolveInfo target=visible.get(which);Intent launch=new Intent(Intent.ACTION_MAIN);launch.addCategory(Intent.CATEGORY_LAUNCHER);launch.setClassName(target.activityInfo.packageName,target.activityInfo.name);
            try{startActivity(launch);}catch(Exception ex){Toast.makeText(this,"Could not open this app.",Toast.LENGTH_SHORT).show();}
        }).setNegativeButton("Cancel",null).show();
    }
    private void pickMusic(){
        try{Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("audio/*");i.putExtra(Intent.EXTRA_ALLOW_MULTIPLE,true);i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION|Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION);startActivityForResult(i,PICK_AUDIO);}
        catch(Exception ex){Toast.makeText(this,"No Android file picker is available on this unit.",Toast.LENGTH_LONG).show();}
    }
    @Override protected void onActivityResult(int request,int result,Intent data){
        super.onActivityResult(request,result,data);if(request!=PICK_AUDIO)return;if(result!=RESULT_OK||data==null){startAfterPick=false;return;}
        ArrayList<Uri> chosen=new ArrayList<>();if(data.getClipData()!=null){for(int i=0;i<data.getClipData().getItemCount();i++)chosen.add(data.getClipData().getItemAt(i).getUri());}else if(data.getData()!=null)chosen.add(data.getData());
        if(chosen.isEmpty())return;songs.clear();songs.addAll(chosen);index=0;
        for(Uri uri:songs){try{getContentResolver().takePersistableUriPermission(uri,data.getFlags()&Intent.FLAG_GRANT_READ_URI_PERMISSION);}catch(SecurityException ignored){}}
        JSONArray saved=new JSONArray();for(Uri uri:songs)saved.put(uri.toString());prefs.edit().putString("songs",saved.toString()).putInt("index",0).apply();
        boolean startSelected=startAfterPick;startAfterPick=false;load(startSelected);if(web!=null)web.evaluateJavascript("window.DEHReturnToPlayer&&window.DEHReturnToPlayer()",null);
    }
    private void restoreSongs(){try{JSONArray a=new JSONArray(prefs.getString("songs","[]"));for(int i=0;i<a.length();i++)songs.add(Uri.parse(a.getString(i)));index=Math.max(0,Math.min(prefs.getInt("index",0),songs.size()-1));}catch(Exception ignored){songs.clear();index=0;}}
    private void releasePlayer(){if(player!=null){try{player.reset();}catch(Exception ignored){}player.release();player=null;}ready=false;preparing=false;}
    private void load(boolean start){
        generation++;final int token=generation;releasePlayer();playWhenReady=start;state="loading";message="";
        if(songs.isEmpty()){state="stopped";sendState();return;}
        index=Math.max(0,Math.min(index,songs.size()-1));prefs.edit().putInt("index",index).apply();
        try{MediaPlayer m=new MediaPlayer();player=m;m.setAudioStreamType(AudioManager.STREAM_MUSIC);m.setDataSource(this,songs.get(index));preparing=true;
            m.setOnPreparedListener(p->{if(token!=generation||player!=p)return;preparing=false;ready=true;state="paused";if(playWhenReady)start();else sendState();});
            m.setOnCompletionListener(p->{if(token!=generation||player!=p)return;if(index+1<songs.size()){index++;load(true);}else{state="stopped";try{p.seekTo(0);}catch(Exception ignored){}sendState();}});
            m.setOnErrorListener((p,what,extra)->{if(token==generation){releasePlayer();state="error";message="Audio file could not be played. Choose another file.";sendState();}return true;});
            m.prepareAsync();sendState();
        }catch(Exception ex){releasePlayer();state="error";message="Cannot open this audio file. Choose it again.";sendState();}
    }
    private void start(){if(!ready||player==null)return;if(audio.requestAudioFocus(focus,AudioManager.STREAM_MUSIC,AudioManager.AUDIOFOCUS_GAIN)!=AudioManager.AUDIOFOCUS_REQUEST_GRANTED){message="Audio focus unavailable.";sendState();return;}try{player.start();state="playing";message="";}catch(Exception ex){state="error";message="Could not start playback.";}sendState();}
    private void perform(String command){
        if("play".equals(command)){if(songs.isEmpty()){startAfterPick=true;pickMusic();return;}if(ready)start();else if(preparing)playWhenReady=true;else load(true);}
        else if("pause".equals(command)){playWhenReady=false;if(player!=null&&ready){try{if(player.isPlaying())player.pause();}catch(Exception ignored){}}state="paused";sendState();}
        else if("stop".equals(command)){playWhenReady=false;if(player!=null&&ready){try{if(player.isPlaying())player.pause();player.seekTo(0);}catch(Exception ignored){}}state="stopped";audio.abandonAudioFocus(focus);sendState();}
        else if("next".equals(command)||"previous".equals(command)){if(songs.isEmpty()){pickMusic();return;}boolean resume="playing".equals(state)||playWhenReady;index=(index+("next".equals(command)?1:-1)+songs.size())%songs.size();load(resume);}
    }
    private String title(Uri uri){try(Cursor c=getContentResolver().query(uri,new String[]{OpenableColumns.DISPLAY_NAME},null,null,null)){if(c!=null&&c.moveToFirst()){String x=c.getString(0);int dot=x.lastIndexOf('.');return dot>0?x.substring(0,dot):x;}}catch(Exception ignored){}return "Audio file";}
    private void requestTitle(Uri uri){String key=uri.toString();if(key.equals(cachedTitleUri))return;cachedTitleUri=key;cachedTitle="Audio file";fileTasks.execute(()->{String name=title(uri);runOnUiThread(()->{if(key.equals(cachedTitleUri)){cachedTitle=name;sendState();}});});}
    private void sendState(){if(!pageReady||web==null)return;if(!songs.isEmpty())requestTitle(songs.get(index));JSONObject j=new JSONObject();try{j.put("title",songs.isEmpty()?"Select music":cachedTitle);j.put("album",songs.isEmpty()?"Choose audio files from Source": "Android audio files");j.put("index",songs.isEmpty()?0:index+1);j.put("count",songs.size());j.put("state",state);j.put("message",message);j.put("position",ready&&player!=null?player.getCurrentPosition()/1000:0);j.put("duration",ready&&player!=null?player.getDuration()/1000:0);int max=audio.getStreamMaxVolume(AudioManager.STREAM_MUSIC);j.put("volume",max>0?Math.round(100f*audio.getStreamVolume(AudioManager.STREAM_MUSIC)/max):0);}catch(Exception ignored){}web.evaluateJavascript("window.DEHAndroidUpdate&&window.DEHAndroidUpdate("+j+")",null);}
}
