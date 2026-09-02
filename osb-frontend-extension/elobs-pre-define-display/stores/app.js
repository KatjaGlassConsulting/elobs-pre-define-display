// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Katja Glass Consulting

import { i18n } from '@/plugins/i18n'

export default {
  menuItems: {
    Studies: {
      items: [
        {
          title: i18n.t('ElobsPreDefineDisplay.menu_label'),
          url: { name: 'ElobsPreDefineDisplay' },
          icon: 'mdi-eye-outline',
        },
      ],
    },
  },
}
