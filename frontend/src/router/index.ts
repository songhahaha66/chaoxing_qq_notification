import { createRouter, createWebHistory, type RouteLocationNormalized } from 'vue-router';
import HomeView from '../views/HomeworkView.vue';
import LoginView from '../views/login.vue'; // Eager load login for immediate redirect
import AboutView from '../views/AboutView.vue';
import DetailInfoView from '../views/DetailInfo.vue';
import { useAuthStore } from '@/stores/auth';

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
    meta: { requiresAuth: true },
  },
  {
    path: '/about',
    name: 'about',
    component: AboutView, // Or lazy load: () => import('../views/AboutView.vue')
    meta: { requiresAuth: true }, // Assuming about page also requires auth
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { guestOnly: true }, // For routes accessible only by unauthenticated users
  },
  {
    path: '/detail/:id',
    name: 'detail',
    component: DetailInfoView, // Or lazy load: () => import('../views/DetailInfo.vue')
    meta: { requiresAuth: true },
  },
  // Fallback route for unmatched paths (optional)
  // { path: '/:pathMatch(.*)*', name: 'NotFound', component: () => import('../views/NotFoundView.vue') }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

router.beforeEach((to: RouteLocationNormalized, from: RouteLocationNormalized, next: Function) => {
  const authStore = useAuthStore();

  // Check if Pinia store is initialized, this can be an issue with HMR or page reloads sometimes.
  // A more robust check might involve ensuring the store instance is available.
  if (!authStore) {
    // If store is not ready, maybe redirect to a loading page or retry logic
    // For now, let's assume it will be ready or proceed with caution.
    // This scenario is less likely if Pinia is set up correctly in main.ts
    console.warn('Auth store not available during navigation guard');
    // Potentially, if access_token exists in localStorage, try to initialize store or redirect to login
    if (localStorage.getItem('access_token')) {
        // Attempt to re-initialize or wait. For now, just proceed.
    } else if (to.meta.requiresAuth) {
        next({ name: 'login', query: { redirect: to.fullPath } });
        return;
    }
  }

  const isAuthenticated = authStore.isAuthenticated;

  if (to.meta.requiresAuth && !isAuthenticated) {
    // If route requires auth and user is not authenticated, redirect to login
    next({ name: 'login', query: { redirect: to.fullPath } });
  } else if (to.meta.guestOnly && isAuthenticated) {
    // If route is for guests only (like login page) and user is authenticated, redirect to home
    next({ name: 'home' });
  } else {
    // Otherwise, allow navigation
    next();
  }
});

export default router;

