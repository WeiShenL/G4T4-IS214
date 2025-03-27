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



DROP TABLE IF EXISTS public.restaurant CASCADE;
DROP TABLE IF EXISTS public.reservation CASCADE;

-- Restaurant Table
CREATE TABLE public.restaurant (
  restaurant_id SERIAL PRIMARY KEY,
  capacity INTEGER NOT NULL,
  availability BOOLEAN NOT NULL,
  name VARCHAR(255) NOT NULL,
  address TEXT NOT NULL,
  rating VARCHAR(50) NOT NULL,
  cuisine VARCHAR(255) NOT NULL
);

-- Reservation Table with UUID for Supabase user_id
CREATE TABLE public.reservation (
  reservation_id SERIAL PRIMARY KEY,
  restaurant_id INTEGER NOT NULL,
  user_id UUID REFERENCES auth.users(id),  -- Changed to UUID to match Supabase auth
  table_no INTEGER,
  status VARCHAR(255) NOT NULL,
  count INTEGER DEFAULT 10,
  price DECIMAL(10,2),
  time TIMESTAMP,
  stripe_payment_id VARCHAR(255),
  FOREIGN KEY (restaurant_id) REFERENCES public.restaurant(restaurant_id)
);

-- -- Reset the sequence for reservation table
-- SELECT setval('reservation_reservation_id_seq', (SELECT COALESCE(MAX(reservation_id), 0) + 1 FROM reservation), false);

-- Enable Row Level Security
ALTER TABLE public.restaurant ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reservation ENABLE ROW LEVEL SECURITY;

-- Restaurant Policies
CREATE POLICY "Public read access for restaurants"
ON public.restaurant FOR SELECT
USING (true);  -- Everyone can read restaurant data

CREATE POLICY "Admin restaurant management"
ON public.restaurant FOR ALL
USING (auth.role() = 'service_role' OR auth.role() = 'authenticated' AND auth.uid() IN (
  SELECT user_id FROM user_types WHERE user_type = 'admin'
));

-- Reservation Policies
CREATE POLICY "Users can view their own reservations"
ON public.reservation FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own reservations"
ON public.reservation FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own reservations"
ON public.reservation FOR UPDATE
USING (auth.uid() = user_id);

CREATE POLICY "Service role can manage all reservations"
ON public.reservation FOR ALL
USING (auth.role() = 'service_role');

-- Initial Restaurant Data
INSERT INTO public.restaurant (restaurant_id, capacity, availability, name, address, rating, cuisine) VALUES
(1, 50, true, 'Ocean View Diner', '123 Seaside Lane', '4.5', 'Seafood'),
(2, 30, true, 'Mountain Grill', '456 Highland Rd', '4.7', 'Steakhouse'),
(3, 100, true, 'City Central Buffet', '789 Downtown Ave', '4.2', 'Buffet'),
(4, 25, false, 'Hidden Sushi Spot', '12 Sakura St', '4.9', 'Japanese'),
(5, 40, true, 'Pasta Paradise', '33 Italian Blvd', '4.3', 'Italian'),
(6, 60, false, 'BBQ Pit Masters', '55 Smokehouse Lane', '4.6', 'Barbecue');

-- Reset sequence to continue after the last inserted ID
SELECT setval('public.restaurant_restaurant_id_seq', (SELECT MAX(restaurant_id) FROM public.restaurant));