import { useState } from 'react';
import type { ReadingRead } from '../api';
import { ReadingForm } from '../components/ReadingForm';
import { ReadingResult } from '../components/ReadingResult';

export function OraclePage() {
  const [reading, setReading] = useState<ReadingRead | null>(null);

  return (
    <main
      style={{
        minHeight: '100dvh',
        paddingTop: 'var(--space-24)',
        paddingBottom: 'var(--space-16)',
        position: 'relative',
      }}
      aria-label="Oracle consultation"
    >
      {/* Background ambient layer */}
      <div
        aria-hidden="true"
        style={{
          position: 'fixed',
          inset: 0,
          background: `
            radial-gradient(ellipse at 20% 80%, rgba(13, 21, 32, 0.8) 0%, transparent 60%),
            radial-gradient(ellipse at 80% 10%, rgba(74, 50, 114, 0.08) 0%, transparent 50%)
          `,
          pointerEvents: 'none',
          zIndex: 0,
        }}
      />
      <div className="fog-layer" aria-hidden="true" />

      <div className="container" style={{ position: 'relative', zIndex: 2 }}>
        {/* Masthead — only on empty state */}
        {!reading && (
          <header style={{ textAlign: 'center', marginBottom: 'var(--space-12)' }}>
            <p
              className="font-ornament text-sm text-brass"
              style={{ letterSpacing: '0.3em', textTransform: 'uppercase', marginBottom: 'var(--space-4)' }}
            >
              Lord of the Mysteries
            </p>
            <h1
              className="font-display text-4xl text-parchment"
              style={{
                fontStyle: 'italic',
                lineHeight: 'var(--leading-tight)',
                marginBottom: 'var(--space-4)',
              }}
            >
              The Tarot Oracle
            </h1>
            <div className="ornament-divider" style={{ maxWidth: '24rem', margin: 'var(--space-4) auto var(--space-6)' }}>
              of Backlund
            </div>
            <p
              className="font-body text-md text-muted italic"
              style={{ maxWidth: '32rem', margin: '0 auto', lineHeight: 'var(--leading-relaxed)' }}
            >
              Peer through the Fog of History. The Tarot cards do not foretell fate — they illuminate
              the forces already at work beneath the gaslit streets of Backlund.
            </p>
          </header>
        )}

        {!reading ? (
          <ReadingForm onComplete={setReading} />
        ) : (
          <ReadingResult
            reading={reading}
            onNewReading={() => setReading(null)}
          />
        )}
      </div>
    </main>
  );
}
