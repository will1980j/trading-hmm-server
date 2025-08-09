# Supabase Setup Guide

## 1. Create Supabase Account
1. Go to https://supabase.com
2. Sign up with GitHub (free)
3. Create new project

## 2. Get Your Credentials
1. Go to Project Settings > API
2. Copy your Project URL and anon public key
3. Update `.env` file:
```
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
```

## 3. Create Tables
1. Go to SQL Editor in Supabase dashboard
2. Copy and paste contents of `database/setup_tables.sql`
3. Click "Run"

## 4. Install Dependencies
```bash
pip install -r requirements.txt
```

## 5. Run Your App
```bash
python hmm_server_with_db.py
```

## 6. Test Database
- Visit http://localhost:5000
- Send webhook data to test storage
- Check Supabase dashboard to see data

## Free Tier Limits
- 500MB database storage
- 2GB bandwidth per month
- 50,000 monthly active users
- Perfect for your trading system!

## Next Steps
- Set up real-time subscriptions
- Add authentication if needed
- Deploy to Vercel/Railway for free hosting