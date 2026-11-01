# ChatGPT Browser Android

Experimental Android WebView wrapper for https://chatgpt.com. The login provider may reject embedded WebViews. Debug signed, not signed for production and not affiliated with OpenAI.

## Files

- `app/` — Android application source and resources.
- `build.gradle`, `settings.gradle`, `gradle.properties` — Gradle build configuration.

## Build

From the repository root:

```sh
cd chatgptbrowser
gradle --no-daemon assembleDebug
```

Output: `app/build/outputs/apk/debug/app-debug.apk`, relative to `chatgptbrowser/`.

Alternatively, GitHub Actions > Android APK > latest run > artifact `chatgpt-browser-debug-apk`.
