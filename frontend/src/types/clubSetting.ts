export interface ClubSetting {
  id: string
  setting_key: string

  club_name: string
  branch: string
  lottery_ticket_price: string

  created_at: string
  updated_at: string
}

export interface ClubSettingUpdate {
  club_name?: string
  branch?: string
  lottery_ticket_price?: number
}