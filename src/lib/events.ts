// Helper untuk koleksi event/agenda.
//
// Status dihitung otomatis dari tanggal + jam (WIB / UTC+7):
//   - "dibuka"  : belum mulai
//   - "berlangsung": sedang berjalan (hari ini, dalam rentang jam)
//   - "selesai" : sudah lewat
// Bisa ditimpa manual lewat `statusOverride` di frontmatter.

export type EventStatus = "dibuka" | "berlangsung" | "selesai" | "ditutup";

export interface EventData {
  title: string;
  description: string;
  type: string;
  startDate: Date;
  endDate?: Date;
  time?: string;
  mode: string;
  location: string;
  price: string;
  speaker?: string;
  registrationUrl?: string;
  registrationNote?: string;
  cover?: string;
  featured?: boolean;
  statusOverride?: EventStatus;
}

export interface EventEntry {
  id: string;
  data: EventData;
}

/** Jam WIB (UTC+7) — sama di semua server, tidak tergantung zona host. */
function nowWIB(): { y: number; m: number; d: number; h: number; min: number } {
  const n = new Date(Date.now() + 7 * 60 * 60 * 1000);
  return {
    y: n.getUTCFullYear(),
    m: n.getUTCMonth(),
    d: n.getUTCDate(),
    h: n.getUTCHours(),
    min: n.getUTCMinutes(),
  };
}

function dayStart(d: Date): number {
  // Awal hari (WIB) dari sebuah tanggal, dalam epoch ms.
  return Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate()) - 7 * 3600_000;
}

/** Parse "09:00 - 15:00 WIB" → { start: 9*60+0, end: 15*60+0 } (menit WIB). */
function parseTime(t?: string): { start: number; end: number } | null {
  if (!t) return null;
  const found = [...t.matchAll(/(\d{1,2})[:.](\d{2})/g)].map(
    (m) => parseInt(m[1], 10) * 60 + parseInt(m[2], 10)
  );
  if (!found.length) return null;
  return { start: found[0], end: found[1] ?? found[0] + 120 };
}

export function eventStatus(e: EventEntry): EventStatus {
  if (e.data.statusOverride) return e.data.statusOverride;

  const now = nowWIB();
  const nowMin = now.h * 60 + now.min;
  const start = dayStart(e.data.startDate);
  const end = dayStart(e.data.endDate ?? e.data.startDate) + 24 * 3600_000;

  // Awal hari ini (WIB)
  const todayStart = Date.UTC(now.y, now.m, now.d) - 7 * 3600_000;
  const nowMs = Date.now();

  // Event satu hari dengan jam → bisa "berlangsung" presisi
  if (!e.data.endDate) {
    const t = parseTime(e.data.time);
    if (t) {
      const startMs = dayStart(e.data.startDate) + t.start * 60_000;
      const endMs = dayStart(e.data.startDate) + t.end * 60_000;
      if (nowMs >= startMs && nowMs <= endMs) return "berlangsung";
      if (nowMs < startMs) return "dibuka";
      return "selesai";
    }
  }

  // Multi-hari
  if (nowMs >= todayStart && nowMs >= start && nowMs < end) return "berlangsung";
  if (nowMs < start) return "dibuka";
  return "selesai";
}

export const STATUS_LABEL: Record<EventStatus, string> = {
  dibuka: "Pendaftaran Dibuka",
  berlangsung: "Sedang Berlangsung",
  selesai: "Selesai",
  ditutup: "Pendaftaran Ditutup",
};

export const TYPE_LABEL: Record<string, string> = {
  workshop: "Workshop",
  bootcamp: "Bootcamp",
  webinar: "Webinar",
  meetup: "Meetup",
  pelatihan: "Pelatihan",
  lainnya: "Kegiatan",
};

export const MODE_LABEL: Record<string, string> = {
  online: "Online",
  offline: "Offline",
  hybrid: "Hybrid",
};

/** Event yang belum selesai, diurutkan dari yang paling dekat. */
export function upcoming(events: EventEntry[]): EventEntry[] {
  return events
    .filter((e) => {
      const s = eventStatus(e);
      return s === "dibuka" || s === "berlangsung";
    })
    .sort((a, b) => a.data.startDate.valueOf() - b.data.startDate.valueOf());
}

/** Event yang sudah lewat, diurutkan dari yang paling baru. */
export function past(events: EventEntry[]): EventEntry[] {
  return events
    .filter((e) => eventStatus(e) === "selesai")
    .sort((a, b) => b.data.startDate.valueOf() - a.data.startDate.valueOf());
}

export function fmtDate(d: Date): string {
  return d.toLocaleDateString("id-ID", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}

export function fmtDateShort(d: Date): string {
  return d.toLocaleDateString("id-ID", { day: "numeric", month: "short", year: "numeric" });
}