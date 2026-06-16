# Sekolah AI

Website ekosistem belajar AI yang dibangun dengan **Astro**, **TailwindCSS v4**, dan **Decap CMS (NetlifyCMS)**. Responsif untuk HP, tablet, dan desktop.

## Halaman

- Home (`/`)
- Tentang (`/tentang`)
- Blog (`/blog`) — dikelola via CMS
- Produk (`/produk`)
- Komunitas (`/komunitas`)
- Kontak (`/kontak`) — form Netlify

## Perintah

| Perintah          | Aksi                                |
| ----------------- | ----------------------------------- |
| `npm run dev`     | Jalankan server dev di `localhost:4321` |
| `npm run build`   | Build situs ke `./dist/`            |
| `npm run preview` | Preview hasil build                 |

## CMS

Panel admin tersedia di `/admin`. Menggunakan Decap CMS dengan `git-gateway`.
Aktifkan **Netlify Identity** + **Git Gateway** di dashboard Netlify untuk mulai
mengelola artikel blog.
