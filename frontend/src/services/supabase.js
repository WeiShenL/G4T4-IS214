import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://gcdwnykubjslnowtlkoh.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdjZHdueWt1YmpzbG5vd3Rsa29oIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDIwMjQ3NTYsImV4cCI6MjA1NzYwMDc1Nn0.kNbTXvXfhMX-ZIhiPJE8jWcc7hGmPXvnHxSXY4ZeOXM';

// Create and export the Supabase client
export const supabase = createClient(supabaseUrl, supabaseKey);
export const supabaseClient = supabase; // For backward compatibility

// Get the current authenticated user
export const getCurrentUser = async () => {
  const { data, error } = await supabase.auth.getSession();
  
  if (error || !data.session) {
    return null;
  }
  
  return data.session.user;
};

// Get user type
export const getUserType = async (userId) => {
  if (!userId) {
    const user = await getCurrentUser();
    if (!user) throw new Error('No authenticated user found');
    userId = user.id;
  }
  
  const { data, error } = await supabase
    .from('user_types')
    .select('user_type')
    .eq('user_id', userId)
    .single();
  
  if (error || !data) {
    throw new Error('Unable to determine user type');
  }
  
  return data.user_type;
};

// Get user profile
export const getUserProfile = async () => {
  const user = await getCurrentUser();
  
  if (!user) {
    throw new Error('No authenticated user found');
  }
  
  const userType = await getUserType(user.id);
  const tableName = userType === 'customer' ? 'customer_profiles' : 'driver_profiles';
  
  const { data, error } = await supabase
    .from(tableName)
    .select('*')
    .eq('id', user.id)
    .single();
  
  if (error) {
    throw error;
  }
  
  return { profile: data, userType };
};

// Sign up
export const signUp = async (email, password, userData) => {
  if (!userData.user_type) {
    throw new Error('User type is required for signup');
  }
  
  const { data, error } = await supabase.auth.signUp({
    email,
    password,
    options: {
      data: userData
    }
  });
  
  if (error) {
    throw error;
  }
  
  return { data, error: null };
};

// Sign in
export const signIn = async (email, password) => {
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password
  });
  
  if (error) {
    throw error;
  }
  
  return { data, error: null };
};

// Sign out
export const signOut = async () => {
  const { error } = await supabase.auth.signOut();
  
  if (error) {
    throw error;
  }
  
  return { error: null };
};