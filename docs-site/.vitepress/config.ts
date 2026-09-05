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
      { text: 'ACAMIS', link: '/task-3-acamis/overview' },
      { text: 'Reference', link: '/reference/standard-tmt-topology' },
      { text: 'Project', link: '/project/architecture' },
      { text: 'v1.0.0-mvp', items: [
        { text: 'Commit: 416cec9', link: 'https://github.com/prabhasb06/steelsim/commit/416cec95e3717c4081d689d9bd84329d30ffcba9' },
        { text: 'Local Backend (8000)', link: 'http://127.0.0.1:8000/api/health' },
        { text: 'Local Frontend (5173)', link: 'http://localhost:5173/' }
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
          text: 'Task 3 — ACAMIS Intelligence',
          collapsed: false,
          items: [
            { text: '26. ACAMIS overview', link: '/task-3-acamis/overview' },
            { text: '27. Architecture & data flow', link: '/task-3-acamis/architecture' },
            { text: '28. Operating modes & risk gates', link: '/task-3-acamis/operating-modes' },
            { text: '29. Scenario Control', link: '/task-3-acamis/scenario-control' },
            { text: '30. Automatic monitoring', link: '/task-3-acamis/automatic-monitoring' },
            { text: '31. Incident response & recovery', link: '/task-3-acamis/incident-response' },
            { text: '32. Advisory Model Gateway', link: '/task-3-acamis/model-gateway' },
            { text: '33. User interface', link: '/task-3-acamis/user-interface' },
            { text: '34. ACAMIS REST API', link: '/task-3-acamis/api-reference' },
            { text: '35. Testing & verification', link: '/task-3-acamis/testing' },
            { text: '36. Investor demonstration', link: '/task-3-acamis/investor-demo' },
            { text: '37. Limitations & roadmap', link: '/task-3-acamis/limitations-and-roadmap' }
          ]
        },
        {
          text: 'Reference',
          collapsed: false,
          items: [
            { text: '38. Standard TMT topology', link: '/reference/standard-tmt-topology' },
            { text: '39. Equipment catalogue', link: '/reference/equipment-catalogue' },
            { text: '40. REST API', link: '/reference/rest-api' },
            { text: '41. WebSocket API', link: '/reference/websocket-api' },
            { text: '42. Data models', link: '/reference/data-models' },
            { text: '43. Environment variables', link: '/reference/environment-variables' },
            { text: '44. Security', link: '/reference/security' },
            { text: '45. Testing', link: '/reference/testing' },
            { text: '46. Troubleshooting', link: '/reference/troubleshooting' }
          ]
        },
        {
          text: 'Project',
          collapsed: false,
          items: [
            { text: '47. Architecture', link: '/project/architecture' },
            { text: '48. Integration contract', link: '/project/integration' },
            { text: '49. Current limitations', link: '/project/current-limitations' },
            { text: '50. Roadmap', link: '/project/roadmap' },
            { text: '51. Glossary', link: '/project/glossary' },
            { text: '52. MVP readiness', link: '/project/mvp-readiness' }
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