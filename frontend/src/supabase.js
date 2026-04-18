import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://tuqbeulmupthayzzoioa.supabase.co'
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR1cWJldWxtdXB0aGF5enpvaW9hIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU2MDU3NzcsImV4cCI6MjA5MTE4MTc3N30.3g9mYDc4zGPQM23Yf5Ey-Qtkt25XuLkI6V0Cl_UwmM8'

export const supabase = createClient(supabaseUrl, supabaseKey, {
  auth: {
    flowType: 'implicit',
  },
})
