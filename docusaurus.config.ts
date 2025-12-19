import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'Physical AI Textbook',
  tagline: 'Master Humanoid Robotics with ROS 2, Simulation & AI',
  favicon: 'img/robot-icon.webp',

  // Set the production url of your site here
  url: 'https://physical-ai-textbook.example.com',
  baseUrl: '/',

  // GitHub pages deployment config
  organizationName: 'hackathon-physical-ai',
  projectName: 'humanoid-textbook',

  onBrokenLinks: 'warn',

  markdown: {
    hooks: {
      onBrokenMarkdownLinks: 'warn',
    },
  },

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
        },
        blog: {
          showReadingTime: true,
          feedOptions: {
            type: ['rss', 'atom'],
            xslt: true,
          },
        },
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    image: 'img/docusaurus-social-card.jpg',

    // Dark mode as default
    colorMode: {
      defaultMode: 'dark',
      disableSwitch: false,
      respectPrefersColorScheme: false,
    },

    navbar: {
      title: 'Physical AI Textbook',
      style: 'dark',
      logo: {
        alt: 'Physical AI Logo',
        src: 'img/robot-icon.webp',
        srcDark: 'img/robot-icon.webp',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'Chapters',
        },
        {
          to: '/blog',
          label: 'Blog',
          position: 'left',
        },
        {
          href: 'https://github.com/hackathon-physical-ai/humanoid-textbook',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },

    // Minimal 3-column footer
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {
              label: 'Introduction',
              to: '/docs/intro',
            },
            {
              label: 'Chapter 1: ROS 2',
              to: '/docs/chapter-1-ros2-urdf-introduction',
            },
            {
              label: 'Chapter 4: Simulation',
              to: '/docs/chapter-4',
            },
          ],
        },
        {
          title: 'Community',
          items: [
            {
              label: 'ROS Discourse',
              href: 'https://discourse.ros.org/',
            },
            {
              label: 'NVIDIA Isaac',
              href: 'https://developer.nvidia.com/isaac-sim',
            },
            {
              label: 'Robotics Reddit',
              href: 'https://www.reddit.com/r/robotics/',
            },
          ],
        },
        {
          title: 'More',
          items: [
            {
              label: 'Blog',
              to: '/blog',
            },
            {
              label: 'GitHub',
              href: 'https://github.com/umaima-fareed13/physical-ai-humanoid-textbook',
            },
            {
              label: 'NVIDIA Omniverse',
              href: 'https://www.nvidia.com/en-us/omniverse/',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Physical AI Textbook. Built with Docusaurus.`,
    },

    // Dracula theme for code blocks
    prism: {
      theme: prismThemes.dracula,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['bash', 'python', 'yaml', 'markup'],
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
