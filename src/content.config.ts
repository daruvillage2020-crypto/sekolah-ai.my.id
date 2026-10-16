import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";

const blog = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./src/content/blog" }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    date: z.coerce.date(),
    author: z.string().default("Tim Sekolah AI"),
    cover: z.string().optional(),
  }),
});

const events = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./src/content/events" }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    // Jenis kegiatan
    type: z
      .enum(["workshop", "bootcamp", "webinar", "meetup", "pelatihan", "lainnya"])
      .default("lainnya"),
    startDate: z.coerce.date(),
    endDate: z.coerce.date().optional(),
    time: z.string().optional(), // mis. "09:00 - 15:00 WIB"
    // Mode pelaksanaan
    mode: z.enum(["online", "offline", "hybrid"]).default("online"),
    location: z.string().default("Zoom Meeting"),
    price: z.string().default("Gratis"),
    speaker: z.string().optional(),
    // Link pendaftaran (opsional)
    registrationUrl: z.string().optional(),
    registrationNote: z.string().optional(),
    cover: z.string().optional(),
    featured: z.boolean().default(false),
    // Status manual (opsional). Kalau kosong, dihitung otomatis dari tanggal.
    statusOverride: z.enum(["dibuka", "ditutup", "selesai"]).optional(),
  }),
});

export const collections = { blog, events };