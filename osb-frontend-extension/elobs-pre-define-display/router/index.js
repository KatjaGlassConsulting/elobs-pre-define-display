import roles from '@/constants/roles'

const elobsPreDefineDisplayRoute = {
  path: 'elobs-pre-define-display',
  name: 'ElobsPreDefineDisplay',
  component: () => import('../views/ElobsPreDefineDisplayView.vue'),
  meta: {
    resetBreadcrumbs: true,
    authRequired: true,
    section: 'Studies',
    requiredPermission: roles.STUDY_READ,
  },
}

export function addExtensionRoutes(routes) {
  const studiesRoute = routes.find((route) => route.path === '/studies')
  if (studiesRoute?.children) {
    studiesRoute.children.push(elobsPreDefineDisplayRoute)
  }
}
