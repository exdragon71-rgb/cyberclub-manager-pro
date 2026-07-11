import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
} from 'react-router-dom'

import App from './App.tsx'
import './index.css'
import { CreateProductPage } from './pages/CreateProductPage.tsx'
import { DebtsPage } from './pages/DebtsPage.tsx'
import { EditProductPage } from './pages/EditProductPage.tsx'
import { EmployeesPage } from './pages/EmployeesPage.tsx'
import { InventoryPage } from './pages/InventoryPage.tsx'
import { ProductsPage } from './pages/ProductsPage.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />

        <Route
          path="/products"
          element={<ProductsPage />}
        />

        <Route
          path="/products/new"
          element={<CreateProductPage />}
        />

        <Route
          path="/products/:productId/edit"
          element={<EditProductPage />}
        />

        <Route
          path="/inventory"
          element={<InventoryPage />}
        />

        <Route
          path="/employees"
          element={<EmployeesPage />}
        />

        <Route
          path="/debts"
          element={<DebtsPage />}
        />

        <Route
          path="*"
          element={<Navigate to="/" replace />}
        />
      </Routes>
    </BrowserRouter>
  </StrictMode>,
)