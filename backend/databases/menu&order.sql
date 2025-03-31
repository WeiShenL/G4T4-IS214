-- Menu table with required fields
CREATE TABLE IF NOT EXISTS public.menu (
  menu_id SERIAL PRIMARY KEY,
  restaurant_id INTEGER NOT NULL REFERENCES public.restaurant(restaurant_id),
  item_name VARCHAR(255) NOT NULL,
  description TEXT,
  price DECIMAL(10, 2) NOT NULL 
);

-- Order table with required fields
CREATE TABLE IF NOT EXISTS public.orders (
  order_id SERIAL PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES auth.users(id),
  restaurant_id INTEGER NOT NULL REFERENCES public.restaurant(restaurant_id),
  item_name VARCHAR(255) NOT NULL,
  quantity INTEGER NOT NULL,
  order_price DECIMAL(10, 2) NOT NULL,
  -- payment_id VARCHAR(255),
  created_at TIMESTAMP DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE public.menu ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.orders ENABLE ROW LEVEL SECURITY;

-- Menu Policies
-- Everyone can view menu items (public read access)
CREATE POLICY "Public read access for menu items"
ON public.menu FOR SELECT
USING (true);

-- Only service role (admin) can modify menu items
CREATE POLICY "Service role can manage all menu items"
ON public.menu FOR ALL
USING (auth.role() = 'service_role')
WITH CHECK (auth.role() = 'service_role');

-- Orders Policies
-- Users can only view their own orders
CREATE POLICY "Users can view their own orders"
ON public.orders FOR SELECT
USING (auth.uid() = user_id);

-- Users can create their own orders
CREATE POLICY "Users can create their own orders"
ON public.orders FOR INSERT
WITH CHECK (auth.uid() = user_id);

-- Service role can manage all orders (for admin purposes)
CREATE POLICY "Service role can manage all orders"
ON public.orders FOR ALL
USING (auth.role() = 'service_role')
WITH CHECK (auth.role() = 'service_role');

-- Insert sample menu items for existing restaurants
INSERT INTO public.menu (restaurant_id, item_name, description, price) VALUES
(1, 'Seafood Feast', 'Unlimited seafood including lobster, shrimp, and fish tacos.', 49.99),
(2, 'Steak Lovers Buffet', 'Unlimited premium steaks and sides.', 59.99),
(3, 'International Buffet', 'Over 100 dishes from around the world.', 39.99),
(1, 'Asian Fusion Experience', 'A blend of Chinese, Japanese, and Thai cuisines.', 45.99),
(2, 'Mediterranean Delight', 'Authentic dishes from Greece, Italy, and Spain.', 42.99),
(3, 'BBQ Bonanza', 'All-you-can-eat barbecue meats and classic sides.', 47.99),
(1, 'Vegetarian Paradise', 'Diverse selection of plant-based dishes and desserts.', 35.99),
(2, 'Sushi Extravaganza', 'Unlimited sushi rolls, sashimi, and Japanese appetizers.', 54.99),
(3, 'Tex-Mex Fiesta', 'Endless tacos, fajitas, and other Mexican favorites.', 41.99),
(1, 'Breakfast All Day', '24-hour access to breakfast classics and modern twists.', 29.99),
(2, 'Pasta Perfection', 'Variety of pasta dishes with artisanal sauces and toppings.', 38.99),
(3, 'Dim Sum Delights', 'Traditional and fusion dim sum served all day.', 44.99),
(1, 'Burger Bash', 'Gourmet burgers with endless topping combinations.', 36.99),
(2, 'Seafood and Steak Combo', 'The best of land and sea in one package.', 64.99),
(3, 'Indian Spice Journey', 'A tour of India's diverse culinary landscape.', 46.99),
(1, 'Pizza Unlimited', 'Artisanal pizzas with gourmet toppings, fired to perfection.', 37.99),
(2, 'Healthy Living', 'Nutritious and delicious options for health-conscious diners.', 39.99),
(3, 'Dessert Wonderland', 'A sweet tooth's dream with endless dessert options.', 32.99),
(1, 'Farm to Table Fresh', 'Seasonal dishes made with locally-sourced ingredients.', 48.99),
(2, 'Global Street Food', 'Popular street foods from around the world.', 43.99)
