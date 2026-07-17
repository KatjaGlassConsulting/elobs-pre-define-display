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

    <!-- Study + version selection -->
    <v-card elevation="0" rounded="lg" class="mb-4">
      <v-card-text>
        <div class="d-flex align-center">
          <v-autocomplete
            v-model="selectedStudy"
            :items="studies"
            :label="$t('ElobsPreDefineDisplay.study_label')"
            :placeholder="$t('ElobsPreDefineDisplay.study_placeholder')"
            :item-title="studyTitle"
            return-object
            variant="outlined"
            rounded="lg"
            color="nnBaseBlue"
            density="compact"
            autocomplete="off"
            clearable
            hide-details="auto"
            class="mr-4"
            :loading="studiesLoading"
          />
          <v-select
            v-model="version"
            :items="versionItems"
            :label="$t('ElobsPreDefineDisplay.version_label')"
            item-title="title"
            item-value="value"
            variant="outlined"
            rounded="lg"
            color="nnBaseBlue"
            density="compact"
            hide-details="auto"
            style="max-width: 220px"
            :loading="versionsLoading"
            :disabled="!selectedStudy"
          />
        </div>
      </v-card-text>
    </v-card>

    <!-- Study metadata -->
    <v-card v-if="selectedStudy" elevation="0" rounded="lg" class="mb-4">
      <v-card-title class="text-h6">{{ $t('ElobsPreDefineDisplay.metadata_title') }}</v-card-title>
      <v-card-text>
        <v-progress-circular v-if="metadataLoading" indeterminate color="nnBaseBlue" />
        <v-table v-else density="compact">
          <tbody>
            <tr>
              <td class="font-weight-medium" style="width: 220px">{{ $t('ElobsPreDefineDisplay.meta_study_name') }}</td>
              <td>{{ metadata.study_name }}</td>
            </tr>
            <tr>
              <td class="font-weight-medium">{{ $t('ElobsPreDefineDisplay.meta_study_description') }}</td>
              <td>{{ metadata.study_description }}</td>
            </tr>
            <tr>
              <td class="font-weight-medium">{{ $t('ElobsPreDefineDisplay.meta_protocol_name') }}</td>
              <td>{{ metadata.protocol_name }}</td>
            </tr>
            <tr>
              <td class="font-weight-medium">{{ $t('ElobsPreDefineDisplay.meta_version') }}</td>
              <td>{{ metadata.version }}</td>
            </tr>
          </tbody>
        </v-table>
      </v-card-text>
    </v-card>

    <!-- Standard selection -->
    <v-card elevation="0" rounded="lg" class="mb-4">
      <v-card-text>
        <v-autocomplete
          v-model="selectedStandard"
          :items="standards"
          :label="$t('ElobsPreDefineDisplay.standard_label')"
          :placeholder="$t('ElobsPreDefineDisplay.standard_placeholder')"
          :item-title="standardTitle"
          item-value="sponsor_model"
          variant="outlined"
          rounded="lg"
          color="nnBaseBlue"
          density="compact"
          autocomplete="off"
          clearable
          hide-details="auto"
          :loading="standardsLoading"
        />
      </v-card-text>
    </v-card>

    <!-- Datasets -->
    <v-card elevation="0" rounded="lg" class="mb-4">
      <v-card-title class="text-h6">{{ $t('ElobsPreDefineDisplay.datasets_title') }}</v-card-title>
      <v-card-text>
        <div class="text-medium-emphasis mb-2">{{ $t('ElobsPreDefineDisplay.datasets_hint') }}</div>
        <v-data-table
          :headers="datasetHeaders"
          :items="datasets"
          :loading="datasetsLoading"
          density="compact"
          hover
          @click:row="onDatasetClick"
        >
          <template #no-data>{{ $t('ElobsPreDefineDisplay.no_rows') }}</template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <!-- Variables -->
    <v-card v-if="selectedDataset" elevation="0" rounded="lg" class="mb-4">
      <v-card-title class="text-h6">
        {{ $t('ElobsPreDefineDisplay.variables_title') }} — {{ selectedDataset }}
      </v-card-title>
      <v-card-text>
        <v-data-table
          :headers="variableHeaders"
          :items="variables"
          :loading="variablesLoading"
          density="compact"
        >
          <template #no-data>{{ $t('ElobsPreDefineDisplay.no_rows') }}</template>
        </v-data-table>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { notificationHub } from '@/plugins/notificationHub'
import repository from '@/api/repository'
import extensionsApi from '../api/extensions'

const { t } = useI18n()

// Study + version
const studies = ref([])
const studiesLoading = ref(false)
const selectedStudy = ref(null)
const version = ref(null) // null = Latest
const studyVersions = ref([])
const versionsLoading = ref(false)

// Metadata
const metadata = ref({})
const metadataLoading = ref(false)

// Standard
const standards = ref([])
const standardsLoading = ref(false)
const selectedStandard = ref(null)

// Datasets + variables
const datasets = ref([])
const datasetsLoading = ref(false)
const selectedDataset = ref(null)
const variables = ref([])
const variablesLoading = ref(false)

const studyTitle = (s) => [s.id, s.acronym].filter(Boolean).join(' — ')
const standardTitle = (s) =>
  [s.sponsor_model, s.cdisc_ig].filter(Boolean).join('  ·  ')

const versionItems = computed(() => [
  { title: t('ElobsPreDefineDisplay.version_latest'), value: null },
  ...studyVersions.value.map((v) => ({ title: v, value: v })),
])

const datasetHeaders = [
  { title: 'Dataset', key: 'Dataset' },
  { title: 'Description', key: 'Description' },
  { title: 'Class', key: 'Class' },
  { title: 'Structure', key: 'Structure' },
  { title: 'Purpose', key: 'Purpose' },
  { title: 'Keys', key: 'Keys' },
  { title: 'Documentation', key: 'Documentation' },
  { title: 'Location', key: 'Location' },
]

const variableHeaders = [
  { title: 'Variable', key: 'Variable' },
  { title: 'CDISC', key: 'Cdisc' },
  { title: 'Label', key: 'Label' },
  { title: 'Type', key: 'Type' },
  { title: 'Length', key: 'Length' },
  { title: 'Display format', key: 'DisplayFormat' },
  { title: 'Codelist', key: 'Codelist' },
  { title: 'Term', key: 'Term' },
  { title: 'Core', key: 'Core' },
  { title: 'Origin', key: 'Origin' },
  { title: 'Role', key: 'Role' },
  { title: 'Comment', key: 'Comment' },
  { title: 'Order', key: 'Order' },
]

function notifyError() {
  notificationHub.add({ msg: t('ElobsPreDefineDisplay.error_message'), type: 'error' })
}

// Load the study list (native OSB endpoint) and standards (extension) up front.
async function loadStudies() {
  studiesLoading.value = true
  try {
    const { data } = await repository.get('/studies/list')
    studies.value = data.items ?? data
  } catch {
    // best-effort; selector simply shows no options
  } finally {
    studiesLoading.value = false
  }
}

async function loadStandards() {
  standardsLoading.value = true
  try {
    standards.value = await extensionsApi.getStandards()
  } catch {
    notifyError()
  } finally {
    standardsLoading.value = false
  }
}

loadStudies()
loadStandards()

// Study changed -> reload versions + metadata, reset downstream selections.
watch(selectedStudy, async (study) => {
  version.value = null
  studyVersions.value = []
  metadata.value = {}
  selectedDataset.value = null
  variables.value = []
  datasets.value = []
  if (!study) return

  versionsLoading.value = true
  try {
    const { data } = await repository.get(`/studies/${study.uid}/snapshot-history`, {
      params: { page_size: 0 },
    })
    const items = data.items ?? data ?? []
    const seen = new Set()
    studyVersions.value = items
      .map((it) => it?.current_metadata?.version_metadata?.version_number)
      .filter((v) => v != null && v !== '')
      .filter((v) => (seen.has(v) ? false : seen.add(v)))
  } catch {
    // best-effort; user can still use Latest
  } finally {
    versionsLoading.value = false
  }
})

// Study or version changed -> reload metadata + datasets.
watch([selectedStudy, version], async () => {
  await loadMetadata()
  await loadDatasets()
})

// Standard changed -> reload datasets.
watch(selectedStandard, async () => {
  selectedDataset.value = null
  variables.value = []
  await loadDatasets()
})

// Dataset selected -> load its variables.
watch(selectedDataset, async () => {
  variables.value = []
  if (!selectedDataset.value || !selectedStandard.value) return
  variablesLoading.value = true
  try {
    variables.value = await extensionsApi.getVariables(
      selectedDataset.value,
      selectedStandard.value,
    )
  } catch {
    notifyError()
  } finally {
    variablesLoading.value = false
  }
})

async function loadMetadata() {
  if (!selectedStudy.value) return
  metadataLoading.value = true
  try {
    const params = version.value ? { study_value_version: version.value } : {}
    const { data } = await repository.get(`/studies/${selectedStudy.value.uid}`, { params })
    const cm = data?.current_metadata ?? {}
    metadata.value = {
      study_name: cm.identification_metadata?.study_id,
      study_description: cm.study_description?.study_title,
      protocol_name: cm.identification_metadata?.study_acronym,
      version: cm.version_metadata?.version_number,
    }
  } catch {
    notifyError()
  } finally {
    metadataLoading.value = false
  }
}

async function loadDatasets() {
  selectedDataset.value = null
  datasets.value = []
  if (!selectedStudy.value || !selectedStandard.value) return
  datasetsLoading.value = true
  try {
    datasets.value = await extensionsApi.getDatasets(
      selectedStudy.value.uid,
      selectedStandard.value,
      version.value || null,
    )
  } catch {
    notifyError()
  } finally {
    datasetsLoading.value = false
  }
}

function onDatasetClick(_event, { item }) {
  selectedDataset.value = item.Dataset
}
</script>
