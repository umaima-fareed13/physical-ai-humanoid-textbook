import type { ReactNode } from 'react';
import Link from '@docusaurus/Link';
import Layout from '@theme/Layout';

import styles from './index.module.css';

function HeroSection() {
  return (
    <section className={styles.hero}>
      <div className={styles.heroContainer}>
        {/* Left Side - Content */}
        <div className={styles.heroContent}>
          <span className={styles.badge}>Open Source Curriculum</span>
          <h1 className={styles.heroTitle}>
            Physical AI<br />
            <span className={styles.titleAccent}>Mastery</span>
          </h1>
          <p className={styles.heroSubtitle}>
            Master humanoid robotics from the ground up. Learn ROS 2,
            simulation, motion control, and AI—everything you need to
            build intelligent robots that interact with the physical world.
          </p>
          <div className={styles.heroCta}>
            <Link to="/docs/intro" className={styles.primaryButton}>
              Start Learning
            </Link>
            <Link to="/docs/chapter-1-ros2-urdf-introduction" className={styles.secondaryButton}>
              View Roadmap
            </Link>
          </div>
        </div>

        {/* Right Side - Neon Glow Visual */}
        <div className={styles.heroVisual}>
          <div className={styles.glowContainer}>
            <div className={styles.glowCircle} />
            <div className={styles.glowCircleInner} />
            <div className={styles.glowCore} />
          </div>
        </div>
      </div>
    </section>
  );
}

export default function Home(): ReactNode {
  return (
    <Layout
      title="Physical AI Mastery"
      description="Master humanoid robotics with ROS 2, simulation, and AI. Open-source curriculum for building intelligent robots.">
      <main className={styles.main}>
        <HeroSection />
      </main>
    </Layout>
  );
}
