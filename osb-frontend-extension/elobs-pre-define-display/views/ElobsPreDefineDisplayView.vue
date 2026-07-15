<template>
  <div class="px-4">
    <div class="page-title d-flex align-center">
      {{ $t('ElobsPreDefineDisplay.title') }}
    </div>

    <v-alert
      color="nnLightBlue200"
      icon="mdi-information-outline"
      class="text-nnTrueBlue mx-0 my-0 mb-6"
    >
      {{ $t('ElobsPreDefineDisplay.description') }}
    </v-alert>

    <v-card elevation="0" rounded="lg">
      <v-card-title class="text-h6">{{ $t('ElobsPreDefineDisplay.studies_title') }}</v-card-title>
      <v-card-text>
        <v-progress-circular v-if="isLoading" indeterminate color="nnBaseBlue" />

        <div v-else-if="studies.length === 0" class="text-medium-emphasis">
          {{ $t('ElobsPreDefineDisplay.no_studies') }}
        </div>

        <v-table v-else density="compact">
          <thead>
            <tr>
              <th class="text-left">{{ $t('ElobsPreDefineDisplay.col_study_id') }}</th>
              <th class="text-left">{{ $t('ElobsPreDefineDisplay.col_acronym') }}</th>
              <th class="text-left">{{ $t('ElobsPreDefineDisplay.col_uid') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="study in studies" :key="study.uid">
              <td>{{ study.study_id }}</td>
              <td>{{ study.acronym }}</td>
              <td>{{ study.uid }}</td>
            </tr>
          </tbody>
        </v-table>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { notificationHub } from '@/plugins/notificationHub'
import extensionsApi from '../api/extensions'

const { t } = useI18n()

const studies = ref([])
const isLoading = ref(false)

onMounted(async () => {
  isLoading.value = true
  try {
    studies.value = await extensionsApi.getStudies()
  } catch {
    notificationHub.add({ msg: t('ElobsPreDefineDisplay.error_message'), type: 'error' })
  } finally {
    isLoading.value = false
  }
})
</script>
