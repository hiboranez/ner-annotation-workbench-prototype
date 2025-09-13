import { createRouter, createWebHistory } from 'vue-router'
import DataImport from '../views/DataImport.vue'
import DataOverview from '../views/DataOverview.vue'
import DataAnnotation from '../views/DataAnnotation.vue'
import DataExport from '../views/DataExport.vue'

const routes = [
    { path: '/import', component: DataImport },
    { path: '/overview', component: DataOverview },
    { path: '/annotation', component: DataAnnotation },
    { path: '/export', component: DataExport }
]

export default createRouter({
    history: createWebHistory(),
    routes
})
