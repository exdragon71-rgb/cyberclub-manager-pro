export interface BookingNote {
  id: string
  booking_date: string
  content: string

  created_at: string
  updated_at: string
}

export interface BookingNoteUpdate {
  content: string
}
