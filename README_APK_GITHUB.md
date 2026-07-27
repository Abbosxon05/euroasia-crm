# 📱 EuroAsia CRM — GitHub Actions orqali APK yaratish va Yuklab olish

Ushbu loyihaga **GitHub Actions** o'rnatildi! Endi siz loyihani GitHub-ga yuklaganingizda (yoki o'zgarish saqlaganingizda), GitHub avtomatik ravishda **Android APK (`.apk`)** faylini yig'ib beradi.

---

## 🚀 1-Qadam: Loyihani GitHub-ga yuklash (Git Push)

Terminalingizda (yoki VS Code / Git Bash orqali) quyidagi buyruqlarni bajaring:

```bash
git init
git add .
git commit -m "EuroAsia CRM v7.0 Sodda HEMIS va APK Action qo'shildi"
git branch -M main
# Agar hali GitHub-da repo ochmagan bo'lsangiz, yangi repo ochib uning linkini qo'shing:
# git remote add origin https://github.com/USERNAME/REPO_NAME.git
git push -u origin main
```

---

## 📥 2-Qadam: APK faylni yuklab olish (Download APK)

1. **GitHub** saytida o'z reposingizga kiring.
2. Yuqoridagi menudan **`Actions`** bo'limini bosing.
3. Chap tomonda **`📱 Build Android APK`** ishjarayoni (workflow) ko'rinadi. Oxirgi ishlagan (yashil `✓` belgili) jarayonga kiring.
4. Eng pastga tushsangiz, **`Artifacts`** bo'limida quyidagi fayl turadi:
   - 📦 **`EuroAsia-CRM-Android-APK`** (bosing — arxiv sifatida yuklanadi).
5. Yuklab olingan `.zip` fayl ichida tayyor **`app-debug.apk`** fayli bo'ladi!
6. Ushbu APK-ni Android telefoningizga o'tkazing va o'rnating (`O'rnatishga ruxsat berish / Install anyway`).

---

## ⚡ 3-Qadam: Istalgan paytda APK-ni qo'lda yangilash

Agar kodga yangi o'zgarishlar kiritilsa, GitHub Actions o'zi avtomat yangi APK yasaydi. 
Shuningdek, GitHub saytidagi **Actions -> Build Android APK -> Run workflow** tugmasini bosib ham istalgan paytda yangi APK yig'dirib olishingiz mumkin!
