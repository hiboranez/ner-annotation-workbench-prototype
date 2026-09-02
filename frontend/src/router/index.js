// javascript
import {createRouter, createWebHistory} from 'vue-router';
import DataImport from '../views/DataImport.vue';
import DataOverview from '../views/DataOverview.vue';
import DataAnnotation from '../views/DataAnnotation.vue';
import DataExport from '../views/DataExport.vue';
import Login from '../views/Login.vue';
import Register from '../views/Register.vue';
import {useAuthStore} from '@/stores/authStore';

const routes = [
    {path: '/login', component: Login, meta: {guestOnly: true}},
    {path: '/register', component: Register, meta: {guestOnly: true}},
    {path: '/import', component: DataImport, meta: {requiresAuth: true}},
    {path: '/overview', component: DataOverview, meta: {requiresAuth: true}},
    {path: '/annotation', component: DataAnnotation, meta: {requiresAuth: true}},
    {path: '/export', component: DataExport, meta: {requiresAuth: true}},
    {path: '/', redirect: '/import'},
];

const router = createRouter({
    history: createWebHistory(),
    routes
});

router.beforeEach((to) => {
    const auth = useAuthStore();
    auth.load();
    if (to.meta?.requiresAuth && !auth.isAuthenticated) {
        return {path: '/login', query: {redirect: to.fullPath}};
    }
    if (to.meta?.guestOnly && auth.isAuthenticated) {
        return {path: '/import'};
    }
    return true;
});

export default router;
