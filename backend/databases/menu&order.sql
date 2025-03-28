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
  payment_id VARCHAR(255),
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
(1, 'Grilled Salmon', 'Fresh salmon fillet grilled to perfection, served with seasonal vegetables', 24.99),
(1, 'Seafood Pasta', 'Linguine pasta with a mix of shrimp, mussels, and calamari in a rich tomato sauce', 19.99),
(1, 'Lobster Bisque', 'Creamy soup made with lobster stock, aromatic vegetables, and a touch of brandy', 12.99),
(1, 'Fish Tacos', 'Soft corn tortillas filled with grilled fish, cabbage slaw, and chipotle aioli', 16.99),
(1, 'Clam Chowder', 'Traditional New England style clam chowder with potatoes and bacon', 9.99),

(2, 'Ribeye Steak', '12oz prime ribeye steak cooked to your preference, served with mashed potatoes', 29.99),
(2, 'BBQ Ribs', 'Slow-cooked pork ribs glazed with house BBQ sauce, served with coleslaw', 22.99),
(2, 'Grilled Chicken', 'Herb-marinated chicken breast, grilled and served with roasted vegetables', 18.99),
(2, 'Lamb Chops', 'New Zealand lamb chops with mint sauce and rosemary potatoes', 27.99),
(2, 'Mountain Burger', 'Half-pound Angus beef patty with cheddar, bacon, and all the fixings', 16.99),

(3, 'All-You-Can-Eat Buffet', 'Full access to our premium buffet with over 100 items', 34.99),
(3, 'Lunch Buffet Special', 'Weekday lunch buffet access with drinks included', 19.99),
(3, 'Weekend Brunch', 'Special weekend breakfast and lunch items with complimentary mimosa', 24.99),
(3, 'Kids Buffet', 'For children under 12, includes access to kids corner', 12.99),
(3, 'Seniors Special', 'For guests 65 and over, includes coffee or tea', 22.99);