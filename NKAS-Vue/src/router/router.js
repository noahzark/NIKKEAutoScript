import {createRouter, createWebHashHistory} from "vue-router"

import Main from '@/views/main/main.vue'

const router = createRouter({
    routes:
        [
            {
                path: '/',
                component: Main
            },
            {
                path: '/main',
                name: 'Main',
                component: Main
            },
            {
                path: '/setting',
                name: 'Setting',
                redirect: '/general_setting',
                // redirect: '/conversation_setting',
                component: () => import('@/views/main/setting/setting.vue'),
                children: [
                    {
                        path: '/general_setting',
                        name: 'general_setting',
                        component: () => import('@/views/main/setting/general/general.vue'),

                    },
                    {
                        path: '/simulator_setting',
                        name: 'simulator_setting',
                        component: () => import('@/views/main/setting/simulator/simulator_setting.vue'),

                    },
                    {
                        path: '/reward_setting',
                        name: 'reward_setting',
                        component: () => import('@/views/main/setting/reward/reward.vue'),

                    },
                    {
                        path: '/destroy_setting',
                        name: 'destroy_setting',
                        component: () => import('@/views/main/setting/destroy/destroy.vue'),

                    },
                    {
                        path: '/store_setting',
                        name: 'store_setting',
                        component: () => import('@/views/main/setting/store/store.vue'),

                    },
                    {
                        path: '/commission_setting',
                        name: 'commission_setting',
                        component: () => import('@/views/main/setting/commission/commission.vue'),

                    },
                    {
                        path: '/conversation_setting',
                        name: 'conversation_setting',
                        component: () => import('@/views/main/setting/conversation/conversation_setting.vue'),

                    },
                    {
                        path: '/rookie_arena',
                        name: 'rookie_arena',
                        component: () => import('@/views/main/setting/rookiearena/rookiearena.vue'),

                    },
                    {
                        path: '/simulation_room',
                        name: 'simulation_room',
                        component: () => import('@/views/main/setting/simulationroom/simulationroom.vue'),

                    },
                    {
                        path: '/tribe_tower',
                        name: 'tribe_tower',
                        component: () => import('@/views/main/setting/tribe_tower/tribe_tower.vue'),

                    },
                    {
                        path: '/event_setting',
                        name: 'event_setting',
                        component: () => import('@/views/main/setting/event/event_setting.vue'),

                    },
                    {
                        path: '/daily',
                        name: 'daily',
                        component: () => import('@/views/main/setting/daily/daily.vue'),

                    }
                ]
            },
        ],
    history: createWebHashHistory()
})

export default router
