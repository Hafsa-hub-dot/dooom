# ربط القناة ورفع فيديو Shorts تجريبي خاص - مجانًا

## ما تم
- نجح توليد TRY-001.mp4 على GitHub Actions.
- هذا المسار يرفع فيديو **خاصًا فقط** ولا يفعل النشر اليومي أو العام.
- لا تشاركي أي مفتاح أو refresh token داخل محادثة أو ملف GitHub أو لقطة شاشة.

## 1) مشروع Google
1. افتحي https://console.cloud.google.com/projectcreate وأنشئي مشروعًا (مثلا YouTube Shorts Free). لا تربطي بطاقة بنكية.
2. افتحي https://console.cloud.google.com/apis/library/youtube.googleapis.com واختاري المشروع ثم Enable.

## 2) شاشة موافقة OAuth
1. افتحي https://console.cloud.google.com/auth/overview
2. اضغطي Get started إن ظهرت. اسم التطبيق YouTube Shorts Free، بريد الدعم حسابك.
3. Audience: External إن لم يكن حساب مؤسسة داخلية. أضيفي بريدك إلى Test users من https://console.cloud.google.com/auth/audience.
4. Scopes: اسمحي فقط بنطاق https://www.googleapis.com/auth/youtube.upload (الرفع إلى يوتيوب).
5. **تحذير**: وضع Testing يمنح refresh token مدته غالبًا 7 أيام فقط مع صلاحيات يوتيوب. مناسب للاختبار، لا للنشر الدائم.

## 3) بيانات OAuth لتطبيق الويب
1. https://console.cloud.google.com/auth/clients
2. Create client > Web application.
3. Authorized redirect URI: https://developers.google.com/oauthplayground (انسخي حرفيًا).
4. خزّني Client ID و Client secret في جهازك، وليس في الدردشة.

## 4) الحصول على refresh token
1. افتحي https://developers.google.com/oauthplayground/
2. اضغطي ترس الإعدادات، ثم Use your own OAuth credentials وأدخلي Client ID و Client secret من مشروعك فقط.
3. OAuth flow: Server-side؛ Access type: Offline؛ Force prompt: Consent Screen.
4. في Step 1 اكتبي النطاق: https://www.googleapis.com/auth/youtube.upload ثم Authorize APIs.
5. اختاري حساب القناة الصحيح ووافقي على الوصول. قد تحذرك Google من تطبيق غير متحقق؛ تحققي أنه مشروعك.
6. في Step 2 اضغطي Exchange authorization code for tokens.
7. انسخي قيمة Refresh token واحفظيها سرًا على جهازك. **لا ترسليها إلى ChatGPT**.

## 5) حفظ الرموز بأمان في GitHub
في https://github.com/Hafsa-hub-dot/dooom/settings/secrets/actions اختاري New repository secret ثلاث مرات:
- YOUTUBE_CLIENT_ID = Client ID
- YOUTUBE_CLIENT_SECRET = Client secret
- YOUTUBE_REFRESH_TOKEN = Refresh token

لا تحفظي الرموز في GitHub Code أو في ملف README أو في المحادثة.

## 6) الاختبار الفعلي
1. افتحي https://github.com/Hafsa-hub-dot/dooom/actions/workflows/youtube-private-upload.yml
2. اضغطي Run workflow.
3. في confirm_private_upload اكتبي حرفيًا YES_PRIVATE، ثم Run workflow.
4. بعد ظهور علامة خضراء، افتحي ملخص التشغيل؛ يظهر رابط الفيديو في YouTube Studio، وسيكون **Private**.
5. إذا كان زر Run workflow غير ظاهر، افتحي صفحة Actions من متصفح الكمبيوتر أو فعّلي Desktop site على الهاتف.

## تنبيهات
- كل تشغيل لرفع الفيديو ينشئ نسخة جديدة. لا تعيدي التنفيذ بعد النجاح دون قصد.
- ربط قناة مختلفة بحساب Google قد يجعل الرفع يتم في القناة المختارة أثناء منح الإذن؛ راجعي القناة قبل الموافقة.
- في 2026 توجد صفحات Google رسمية مختلفة بشأن تقييد رفع المشاريع غير المدققة إلى Private؛ نختبر Private أولًا قبل أي محاولة نشر عام.
- لا تدخلي بيانات فوترة. API لديها حصة مجانية، وGitHub Actions للمستودعات العامة ضمن سياسة الاستخدام المجاني.
- هذا النموذج لا يفعّل جدولًا يوميًا بعد. يلزم نجاح التجربة ثم ضبط نموذج الإنتاج والموافقة على الجدولة.
