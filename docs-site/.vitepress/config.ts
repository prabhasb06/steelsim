import { defineConfig } from 'vitepress';

export default defineConfig({
  base: process.env.GITHUB_ACTIONS ? '/steelsimdocumentation/' : '/',
  srcExclude: ['**/README.md'],
  title: 'SteelSim',
  description: 'Industrial digital-twin MVP for MSME induction-furnace and TMT rebar manufacturing',
  lang: 'en-US',
  cleanUrls: true,
  lastUpdated: true,
  
  head: [
    ['link', { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' }],
    ['meta', { name: 'theme-color', content: '#10A37F' }]
  ],

  themeConfig: {
    siteTitle: 'SteelSim',
    logo: '/logo.svg',
    
    nav: [
      { text: 'Getting started', link: '/getting-started/introduction' },
      { text: 'Plant Builder', link: '/task-1-builder/overview' },
      { text: 'Simulation', link: '/task-2-simulation/overview' },
      { text: 'Reference', link: '/reference/standard-tmt-topology' },
      { text: 'Project', link: '/project/architecture' },
      { text: 'v1.0.0-mvp', items: [
        { text: 'Commit: e1dad6e', link: 'https://github.com/prabhasb06/steelsim/commit/e1dad6ef603ee8975a8500ab33debb40d1697d46' },
        { text: 'Local Backend (8000)', link: 'http://127.0.0.1:8000/api/health' },
        { text: 'Local Frontend (5173)', link: 'http://127.0.0.1:5173/' }
      ]}
    ],

    sidebar: {
      '/': [
        {
          text: 'Getting started',
          collapsed: false,
          items: [
            { text: '1. Introduction', link: '/getting-started/introduction' },
            { text: '2. What SteelSim solves', link: '/getting-started/what-steelsim-solves' },
            { text: '3. MVP scope', link: '/getting-started/mvp-scope' },
            { text: '4. Quick start', link: '/getting-started/quick-start' },
            { text: '5. Investor demo', link: '/getting-started/investor-demo' }
          ]
        },
        {
          text: 'Task 1 — Plant Builder',
          collapsed: false,
          items: [
            { text: '6. Task 1 overview', link: '/task-1-builder/overview' },
            { text: '7. Engineering canvas', link: '/task-1-builder/engineering-canvas' },
            { text: '8. Equipment library', link: '/task-1-builder/equipment-library' },
            { text: '9. Ports and connections', link: '/task-1-builder/ports-and-connections' },
            { text: '10. Topology validation', link: '/task-1-builder/topology-validation' },
            { text: '11. Auto Connect', link: '/task-1-builder/auto-connect' },
            { text: '12. Auto Layout', link: '/task-1-builder/auto-layout' },
            { text: '13. Auto Setup', link: '/task-1-builder/auto-setup' },
            { text: '14. Save and load', link: '/task-1-builder/save-and-load' },
            { text: '15. Live equipment telemetry', link: '/task-1-builder/live-equipment-telemetry' }
          ]
        },
        {
          text: 'Task 2 — Simulation',
          collapsed: false,
          items: [
            { text: '16. Task 2 overview', link: '/task-2-simulation/overview' },
            { text: '17. Simulation lifecycle', link: '/task-2-simulation/simulation-lifecycle' },
            { text: '18. Deterministic engine', link: '/task-2-simulation/deterministic-engine' },
            { text: '19. Material-flow model', link: '/task-2-simulation/material-flow-model' },
            { text: '20. Utility-capacity model', link: '/task-2-simulation/utility-capacity-model' },
            { text: '21. Equipment interlocks', link: '/task-2-simulation/equipment-interlocks' },
            { text: '22. Simulation Control Center', link: '/task-2-simulation/control-center' },
            { text: '23. WebSocket telemetry', link: '/task-2-simulation/websocket-telemetry' },
            { text: '24. State trace and events', link: '/task-2-simulation/state-trace-and-events' },
            { text: '25. Cleanup and retention', link: '/task-2-simulation/cleanup-and-retention' }
          ]
        },
        {
          text: 'Reference',
          collapsed: false,
          items: [
            { text: '26. Standard TMT topology', link: '/reference/standard-tmt-topology' },
            { text: '27. Equipment catalogue', link: '/reference/equipment-catalogue' },
            { text: '28. REST API', link: '/reference/rest-api' },
            { text: '29. WebSocket API', link: '/reference/websocket-api' },
            { text: '30. Data models', link: '/reference/data-models' },
            { text: '31. Environment variables', link: '/reference/environment-variables' },
            { text: '32. Security', link: '/reference/security' },
            { text: '33. Testing', link: '/reference/testing' },
            { text: '34. Troubleshooting', link: '/reference/troubleshooting' }
          ]
        },
        {
          text: 'Project',
          collapsed: false,
          items: [
            { text: '35. Architecture', link: '/project/architecture' },
            { text: '36. Task 1 & 2 integration', link: '/project/integration' },
            { text: '37. Current limitations', link: '/project/current-limitations' },
            { text: '38. Roadmap', link: '/project/roadmap' },
            { text: '39. Glossary', link: '/project/glossary' },
            { text: '40. MVP readiness', link: '/project/mvp-readiness' }
          ]
        }
      ]
    },

    search: {
      provider: 'local',
      options: {
        detailedView: true
      }
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/prabhasb06/steelsim' }
    ],

    outline: {
      level: [2, 3],
      label: 'On this page'
    },

    docFooter: {
      prev: 'Previous page',
      next: 'Next page'
    },

    footer: {
      message: 'SteelSim is complete and reliable for its defined investor-facing MVP workflow. It is not presented as production-certified industrial control software.',
      copyright: 'Copyright © 2026 SteelSim. Non-certified engineering digital twin.'
    }
  }
});