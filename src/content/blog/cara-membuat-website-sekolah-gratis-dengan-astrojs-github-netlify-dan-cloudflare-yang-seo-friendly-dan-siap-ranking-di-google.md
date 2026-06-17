---
title: Cara Membuat Website Sekolah Gratis dengan AstroJS, GitHub, Netlify dan
  Cloudflare yang SEO Friendly dan Siap Ranking di Google
description: Di era digital saat ini, website sekolah bukan lagi kebutuhan
  tambahan, melainkan kebutuhan utama. Website berfungsi sebagai pusat informasi
  resmi sekolah, media promosi PPDB, sarana komunikasi dengan orang tua, hingga
  tempat publikasi prestasi siswa dan guru.
date: 2026-06-17T14:58:00.000+07:00
author: Tim Sekolah AI
cover: /uploads/chatgpt-image-jun-17-2026-03_01_48-pm.png
---
# Pendahuluan
Di era digital saat ini, website sekolah bukan lagi kebutuhan tambahan, melainkan kebutuhan utama. Website berfungsi sebagai pusat informasi resmi sekolah, media promosi PPDB, sarana komunikasi dengan orang tua, hingga tempat publikasi prestasi siswa dan guru.

Kabar baiknya, sekolah tidak perlu mengeluarkan biaya jutaan rupiah untuk memiliki website profesional. Dengan teknologi modern seperti AstroJS, GitHub, Cloudflare, dan Netlify, Anda dapat membangun website sekolah secara gratis dengan performa yang sangat cepat.

## Mengapa Sekolah Harus Memiliki Website?
- Meningkatkan kredibilitas sekolah
- Mendukung promosi PPDB
- Menampilkan informasi akademik
- Menjadi pusat publikasi kegiatan sekolah
- Mempermudah komunikasi dengan masyarakat
## Teknologi Gratis yang Digunakan

### AstroJS
Framework modern untuk membuat website statis yang sangat cepat dan ramah SEO. Anda bisa mengunjungi website resminya di https://astro.build/. Berikut halaman utama dari website AstroJS.

### GitHub
Digunakan sebagai tempat penyimpanan source code website. Anda dapat mengunjungi websitenya di alamat https://github.com/

### Netlify
Platform hosting gratis yang dapat meng-online-kan website dalam hitungan menit. Anda dapat mengunjungi websitenya di https://www.netlify.com/

### Cloudflare
Membantu meningkatkan keamanan dan kecepatan website. Anda dapat mengunjunginya di https://www.cloudflare.com/

## Langkah-Langkah Pembuatan
#### 1. Install NodeJS
Unduh dan install NodeJS versi terbaru. Link untuk mendapatkan NodeJS terbaru bisa di alamat berikut: https://nodejs.org/en/download. Pada halaman download pilih pilihan seperti gambar berikut.

#### 2. Membuat Project Astro
Sebelum anda memulai membuat project website sekolah menggunakan Astro, tentu butuh text editor seperti VSCode, VIM, Notepad++ dan lain sebagainya. Anda bisa mendownload dan menginstall VSCode misalnya di https://code.visualstudio.com/download. Anda tinggal mendownload sesuai dengan sistem operasi yang gunakan.

Setelah download dan install, buka aplikasi VSCode, pilih terminal di VSCode lalu jalankan perintah berikut:

> npm create astro@latest

Pilih A basic, helpful starter project (recommended)
Setelah anda menjalankan perintah di atas, website template dasar dari Astro sudah terbentuk di project website anda. Berikutnya adalah melakukan develop atau pengembangan lebih lanjut sesuai dengan kebutuhan. 
Sekarang kita akan menggunakan AI sebagai tools untuk pengembangan website. Pada VSCode tentu anda harus melakukan beberapa setingan agar VSCode anda mensupport model AI.
Setelah anda setting VSCode untuk model AI, selanjutnya adalah mengetikan prompt pada AI berikut:
> “Buat website sederhana jangan desain terlalu rumit dengan fitur berikut: "Home
Tentang
Blog
Produk
Komunitas
Kontak" menggunakan stack modern AstroJS, TailwindCSS dan NetlifyCMS untuk digunakan sebagai ekosistem sekolah AI website resposive dapat di sesuaikan dengan layar di hp, tab, dan laptop atau pc.”

Lihat gambar 9 untuk tempat mengetikkan prompt agar AI anda yang mengeksekusi baris-baris kode website yang akan anda buat.

#### 3. Menjalankan Project
Project yang sudah anda buat dapat dijalankan dengan perintah berikut:
> npm run dev

Jika tidak ada error maka tampilan website yang anda buat dibantu tools AI dengan stack AstroJS, TailwindCSS dan DecapCMS akan terlihat seperti gambar 10 berikut.

#### 4. Upload ke GitHub
Jika website sudah siap anda dapat mengupload ke github dengan perintah berikut, tentunya sebelum di upload anda harus punya akun di github terlebih dahulu dan membuat project repository di github.

Buat nama repository dengan klik tombol New lihat gambar 12 berikut:
Nama repositorynya misalnya sekolah-ai.my.id.
Klik tombol Create repository untuk memulai membuat file repo anda di github.

Setelah anda membuat nama repository, selanjutnya adalah buka aplikasi VSCode anda link-kan repo yang sudah anda buat ke VSCode dengan cara berikut:
> git remote add origin https://github.com/daruvillage2020-crypto/sekolah-ai.my.id.git

Lihat gambar 14 untuk melakukan remote repo di github.

git init
git add .
git commit -m "Website Sekolah"
git push

#### 5. Deploy ke Netlify
Hubungkan repository GitHub ke Netlify dan lakukan deploy. Setelah kode-kode website yang sudah dibuat dilokal komputer dan di submit ke repository github, berikutnya adalah membuild ke server netlify agar website dapat di akses secara public.

#### 6. Hubungkan Domain Sekolah
Proses build di netlify selesai berikutnya adalah bagaimana menghubungkan website anda ke domain yang ada sudah beli.
Contoh:
sekolah.sch.id
smkcontoh.sch.id
aretaschool.id
sekolah-ai.my.id

# Optimasi SEO Website Sekolah
Gunakan judul yang relevan
- Tambahkan meta description
- Buat halaman profil sekolah
- Buat artikel rutin setiap minggu
- Optimasi gambar

# Kesimpulan
Dengan AstroJS, GitHub, Netlify, dan Cloudflare, sekolah dapat memiliki website profesional tanpa biaya hosting yang mahal. Selain cepat dan aman, website ini juga sangat ramah SEO sehingga mudah ditemukan di Google.
