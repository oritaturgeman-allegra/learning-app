-- Row Level Security (RLS) Policies for Capital Market Newsletter
-- Run this AFTER supabase_schema.sql in Supabase SQL Editor
--
-- IMPORTANT: This app uses server-side SQLAlchemy with the service_role key,
-- which bypasses RLS. These policies are for:
-- 1. Defense-in-depth security
-- 2. Future client-side access (mobile apps, realtime features)
-- 3. Direct database access via Supabase Dashboard

-- ============================================================================
-- ENABLE RLS ON ALL TABLES
-- ============================================================================

-- Users table - contains personal data
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Newsletters table - can be linked to users
ALTER TABLE newsletters ENABLE ROW LEVEL SECURITY;

-- Podcast generations - tracks per-user usage
ALTER TABLE podcast_generations ENABLE ROW LEVEL SECURITY;

-- Public data tables - RLS enabled for defense-in-depth
ALTER TABLE feed_providers ENABLE ROW LEVEL SECURITY;
ALTER TABLE articles ENABLE ROW LEVEL SECURITY;
ALTER TABLE article_selections ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- SERVICE ROLE POLICIES
-- ============================================================================
-- The service_role key bypasses RLS automatically, but explicit policies
-- ensure clarity and work if RLS is forced in Supabase settings.

-- Users: Service role has full access
CREATE POLICY "service_role_users_all" ON users
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Newsletters: Service role has full access
CREATE POLICY "service_role_newsletters_all" ON newsletters
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Podcast generations: Service role has full access
CREATE POLICY "service_role_podcast_generations_all" ON podcast_generations
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Feed providers: Service role has full access
CREATE POLICY "service_role_feed_providers_all" ON feed_providers
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Articles: Service role has full access
CREATE POLICY "service_role_articles_all" ON articles
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Article selections: Service role has full access
CREATE POLICY "service_role_article_selections_all" ON article_selections
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- ============================================================================
-- ANON/AUTHENTICATED USER POLICIES
-- ============================================================================
-- For future client-side access (not currently used)

-- Users: Authenticated users can only view their own profile
CREATE POLICY "users_select_own" ON users
    FOR SELECT
    TO authenticated
    USING (
        auth.uid()::text = google_id
        OR auth.jwt()->>'email' = email
    );

-- Users: Authenticated users can update their own profile
CREATE POLICY "users_update_own" ON users
    FOR UPDATE
    TO authenticated
    USING (
        auth.uid()::text = google_id
        OR auth.jwt()->>'email' = email
    )
    WITH CHECK (
        auth.uid()::text = google_id
        OR auth.jwt()->>'email' = email
    );

-- Newsletters: Anyone can read (public pre-generated content)
CREATE POLICY "newsletters_select_all" ON newsletters
    FOR SELECT
    TO anon, authenticated
    USING (true);

-- Podcast generations: Users can view their own history
CREATE POLICY "podcast_generations_select_own" ON podcast_generations
    FOR SELECT
    TO authenticated
    USING (
        user_id IN (
            SELECT id FROM users
            WHERE google_id = auth.uid()::text
            OR email = auth.jwt()->>'email'
        )
    );

-- Feed providers: Anyone can read (public RSS feed metadata)
CREATE POLICY "public_read_feed_providers" ON feed_providers
    FOR SELECT
    TO anon, authenticated
    USING (true);

-- Articles: Anyone can read (public news articles)
CREATE POLICY "public_read_articles" ON articles
    FOR SELECT
    TO anon, authenticated
    USING (true);

-- Article selections: Anyone can read (public curated selections)
CREATE POLICY "public_read_article_selections" ON article_selections
    FOR SELECT
    TO anon, authenticated
    USING (true);

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Check RLS is enabled on tables
-- SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'public';

-- List all policies
-- SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual
-- FROM pg_policies WHERE schemaname = 'public';

-- ============================================================================
-- NOTES
-- ============================================================================
--
-- 1. SERVICE ROLE CONNECTION:
--    The app connects with service_role credentials, which bypass RLS.
--    This is the correct pattern for server-side applications.
--
-- 2. ANON KEY:
--    If you expose the anon key to clients (future mobile app), these
--    policies ensure users can only access their own data.
--
-- 3. ARTICLES, FEED_PROVIDERS & ARTICLE_SELECTIONS:
--    RLS enabled for defense-in-depth. Public read access allowed,
--    but writes are restricted to service_role (backend only).
--
-- 4. TESTING RLS:
--    To test policies, use the SQL Editor with different roles:
--    SET ROLE anon;
--    SELECT * FROM users;  -- Should return nothing
--    RESET ROLE;
