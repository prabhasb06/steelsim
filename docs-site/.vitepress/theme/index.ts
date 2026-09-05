import DefaultTheme from 'vitepress/theme';
import './custom.css';
import { onMounted, watch, nextTick } from 'vue';
import { useRoute } from 'vitepress';

export default {
  extends: DefaultTheme,
  setup() {
    const route = useRoute();

    const renderMermaid = async () => {
      if (typeof window === 'undefined') return;
      try {
        const mermaid = (await import('mermaid')).default;
        const isDark = document.documentElement.classList.contains('dark');
        mermaid.initialize({
          startOnLoad: false,
          theme: isDark ? 'dark' : 'neutral',
          securityLevel: 'loose',
          fontFamily: 'Inter, sans-serif'
        });

        await nextTick();
        const elements = document.querySelectorAll('pre.mermaid, div.mermaid');
        if (elements.length > 0) {
          // Process all elements
          await mermaid.run({
            nodes: Array.from(elements) as HTMLElement[]
          });
        }
      } catch (err) {
        console.warn('Mermaid rendering error:', err);
      }
    };

    onMounted(() => {
      renderMermaid();

      // Observer for theme switch
      const observer = new MutationObserver(() => {
        renderMermaid();
      });
      observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
    });

    watch(
      () => route.path,
      () => {
        nextTick(() => renderMermaid());
      }
    );
  }
};