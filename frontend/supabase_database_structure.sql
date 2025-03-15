-- First, drop existing tables if they exist (comment these out if you want to preserve existing data)
DROP TABLE IF EXISTS customer_profiles CASCADE;
DROP TABLE IF EXISTS driver_profiles CASCADE;
DROP TABLE IF EXISTS user_types CASCADE;
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
DROP FUNCTION IF EXISTS handle_new_user_signup();

-- Customer Profiles Table
CREATE TABLE customer_profiles (
  id UUID REFERENCES auth.users(id) PRIMARY KEY,
  customer_name TEXT NOT NULL,
  phone_number BIGINT NOT NULL,
  street_address TEXT NOT NULL,
  postal_code INTEGER NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Driver Profiles Table
CREATE TABLE driver_profiles (
  id UUID REFERENCES auth.users(id) PRIMARY KEY,
  driver_name TEXT NOT NULL,
  phone_number BIGINT NOT NULL,
  street_address TEXT NOT NULL,
  postal_code INTEGER NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Users Type Table (to track which type each user is)
CREATE TABLE user_types (
  user_id UUID REFERENCES auth.users(id) PRIMARY KEY,
  user_type TEXT NOT NULL CHECK (user_type IN ('customer', 'driver'))
);

-- Enable Row Level Security
ALTER TABLE customer_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE driver_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_types ENABLE ROW LEVEL SECURITY;

-- SELECT POLICIES
-- Users can read their own profile
CREATE POLICY "Users can view own customer profile"
ON customer_profiles FOR SELECT
USING (auth.uid() = id);

CREATE POLICY "Users can view own driver profile"
ON driver_profiles FOR SELECT
USING (auth.uid() = id);

CREATE POLICY "Users can view own type"
ON user_types FOR SELECT
USING (auth.uid() = user_id);

-- INSERT POLICIES (these were missing)
-- Allow users to insert their own profiles
CREATE POLICY "Users can insert own customer profile"
ON customer_profiles FOR INSERT
WITH CHECK (auth.uid() = id);

CREATE POLICY "Users can insert own driver profile"
ON driver_profiles FOR INSERT
WITH CHECK (auth.uid() = id);

CREATE POLICY "Users can insert own type"
ON user_types FOR INSERT
WITH CHECK (auth.uid() = user_id);

-- UPDATE POLICIES
-- Users can update their own profile
CREATE POLICY "Users can update own customer profile"
ON customer_profiles FOR UPDATE
USING (auth.uid() = id);

CREATE POLICY "Users can update own driver profile"
ON driver_profiles FOR UPDATE
USING (auth.uid() = id);

-- SECURE DATABASE FUNCTION
-- Create an improved function that uses SECURITY DEFINER to bypass RLS
CREATE OR REPLACE FUNCTION public.handle_new_user_signup()
RETURNS TRIGGER
SECURITY DEFINER  -- This allows the function to bypass RLS
SET search_path = public
LANGUAGE plpgsql
AS $$
DECLARE
  user_type_val TEXT;
  user_name_val TEXT;
  user_phone_val TEXT;
  user_address_val TEXT;
  user_postal_code_val TEXT;
BEGIN
  -- Log the raw metadata for debugging
  RAISE NOTICE 'New user metadata: %', NEW.raw_user_meta_data;
  
  -- Skip if not a proper signup
  IF NEW.raw_user_meta_data IS NULL THEN
    RAISE NOTICE 'No metadata found for user %', NEW.id;
    RETURN NEW;
  END IF;

  -- Extract values with null safety
  user_type_val := NEW.raw_user_meta_data->>'user_type';
  user_name_val := NEW.raw_user_meta_data->>'name';
  user_phone_val := NEW.raw_user_meta_data->>'phone';
  user_address_val := NEW.raw_user_meta_data->>'address';
  user_postal_code_val := NEW.raw_user_meta_data->>'postal_code';
  
  -- Log the extracted values
  RAISE NOTICE 'Extracted data: type=%, name=%, phone=%', 
    user_type_val, user_name_val, user_phone_val;
  
  -- Skip if user_type is not provided
  IF user_type_val IS NULL THEN
    RAISE NOTICE 'No user_type found for user %', NEW.id;
    RETURN NEW;
  END IF;

  -- Insert into user_types with conflict handling
  INSERT INTO user_types (user_id, user_type)
  VALUES (NEW.id, user_type_val)
  ON CONFLICT (user_id) 
  DO UPDATE SET user_type = EXCLUDED.user_type;
  
  -- For customers
  IF user_type_val = 'customer' THEN
    INSERT INTO customer_profiles (
      id,
      customer_name,
      phone_number,
      street_address,
      postal_code
    ) VALUES (
      NEW.id,
      COALESCE(user_name_val, 'Customer'),
      COALESCE(NULLIF(user_phone_val, '')::BIGINT, 0),
      COALESCE(user_address_val, 'Not provided'),
      COALESCE(NULLIF(user_postal_code_val, '')::INTEGER, 0)
    )
    ON CONFLICT (id) 
    DO UPDATE SET 
      customer_name = EXCLUDED.customer_name,
      phone_number = EXCLUDED.phone_number,
      street_address = EXCLUDED.street_address,
      postal_code = EXCLUDED.postal_code,
      updated_at = NOW();
      
  -- For drivers
  ELSIF user_type_val = 'driver' THEN
    INSERT INTO driver_profiles (
      id,
      driver_name,
      phone_number,
      street_address,
      postal_code
    ) VALUES (
      NEW.id,
      COALESCE(user_name_val, 'Driver'),
      COALESCE(NULLIF(user_phone_val, '')::BIGINT, 0),
      COALESCE(user_address_val, 'Not provided'),
      COALESCE(NULLIF(user_postal_code_val, '')::INTEGER, 0)
    )
    ON CONFLICT (id) 
    DO UPDATE SET 
      driver_name = EXCLUDED.driver_name,
      phone_number = EXCLUDED.phone_number,
      street_address = EXCLUDED.street_address,
      postal_code = EXCLUDED.postal_code,
      updated_at = NOW();
  END IF;
  
  RETURN NEW;
EXCEPTION
  WHEN OTHERS THEN
    -- Log the error but don't prevent user creation
    RAISE NOTICE 'Unhandled error in handle_new_user_signup: %', SQLERRM;
    RETURN NEW;
END;
$$;

-- Create trigger to run our function on user creation
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user_signup();

-- Additional policy to allow direct inserts from server-side functions
-- This can be useful if you need to create profiles directly from your app
CREATE POLICY "Service role can manage all profiles"
ON customer_profiles FOR ALL
USING (auth.role() = 'service_role')
WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "Service role can manage all driver profiles"
ON driver_profiles FOR ALL
USING (auth.role() = 'service_role')
WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "Service role can manage all user types"
ON user_types FOR ALL
USING (auth.role() = 'service_role')
WITH CHECK (auth.role() = 'service_role');