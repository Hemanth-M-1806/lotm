import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import type { ReadingRead } from '../api';
import { TarotCard } from './TarotCard';
import { useAuth } from '../contexts/useAuth';

interface ReadingResultProps {
  reading: ReadingRead;
  onNewReading: () => void;
}

const SPREAD_LABELS: Record<string, string> = {
  single_card:  'Single Card',
  three_card:   'Three Card',
  celtic_cross: 'Celtic Cross',
};

export function ReadingResult({ reading, onNewReading }: ReadingResultProps) {
  const { user } = useAuth();
  const navigate = useNavigate();

  // Sequential reveal: each card flips when its predecessor is flipped
  const [flippedCount, setFlippedCount] = useState(0);
  const [showInterpretation, setShowInterpretation] = useState(false);

  const allFlipped = flippedCount >= reading.cards.length;

  const handleCardFlip = (index: number) => {
    // Only allow flipping next card in sequence
    if (index === flippedCount) {
      setFlippedCount(n => n + 1);
    }
  };

  return (
    <section aria-label="Reading result" style={{ width: '100%' }}>
      {/* Header */}
      <div style={{ textAlign: 'center', marginBottom: 'var(--space-6)' }}>
        <p
          className="font-ornament text-sm text-ghost"
          style={{ letterSpacing: '0.15em', textTransform: 'uppercase', marginBottom: 'var(--space-2)' }}
        >
          {SPREAD_LABELS[reading.spread_type] ?? reading.spread_type}
        </p>
        {reading.question && (
          <h2
            className="font-display text-xl text-parchment italic"
            style={{ lineHeight: 'var(--leading-tight)' }}
          >
            &ldquo;{reading.question}&rdquo;
          </h2>
        )}
        {!reading.question && (
          <h2
            className="font-display text-xl text-muted italic"
            style={{ lineHeight: 'var(--leading-tight)' }}
          >
            Silent Consultation
          </h2>
        )}
      </div>

      {/* Hint for first card */}
      {flippedCount === 0 && (
        <p
          className="font-ornament text-sm text-ghost"
          style={{ textAlign: 'center', letterSpacing: '0.1em', marginBottom: 'var(--space-4)' }}
          aria-live="polite"
        >
          Click the first card to begin the reveal
        </p>
      )}

      {/* Spread */}
      <div className="spread-layout" role="list" aria-label="Drawn cards">
        {reading.cards.map((rc, i) => (
          <div key={rc.id} className="spread-position" role="listitem">
            <div className="spread-position__label">{rc.position_name}</div>
            <TarotCard
              card={rc}
              isFlipped={i < flippedCount}
              onFlip={() => handleCardFlip(i)}
            />
            {i < flippedCount && rc.card && (
              <div style={{ textAlign: 'center', maxWidth: '180px' }}>
                <p
                  className="text-xs text-brass"
                  style={{ letterSpacing: '0.12em', textTransform: 'uppercase', marginTop: 'var(--space-2)', marginBottom: 'var(--space-1)' }}
                >
                  {rc.is_reversed ? 'Reversed' : 'Upright'}
                </p>
                <p
                  className="text-sm text-parchment"
                  style={{ fontStyle: 'italic', lineHeight: 'var(--leading-relaxed)' }}
                >
                  {rc.is_reversed ? rc.card.reversed_meaning : rc.card.upright_meaning}
                </p>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Reveal interpretation after all cards flipped */}
      {allFlipped && !showInterpretation && (
        <div style={{ textAlign: 'center', marginTop: 'var(--space-8)' }}>
          <div className="ornament-divider" style={{ marginBottom: 'var(--space-6)' }}>
            Synthesis awaits
          </div>
          <button
            className="btn btn--ghost"
            onClick={() => setShowInterpretation(true)}
          >
            Receive the Interpretation
          </button>
        </div>
      )}

      {showInterpretation && reading.interpretation && (
        <div className="interpretation" aria-live="polite">
          <div className="interpretation__header">
            ✦ &nbsp;Your Reading&nbsp; ✦
          </div>
          <p className="interpretation__text">{reading.interpretation}</p>
        </div>
      )}

      {/* Actions */}
      <div style={{ display: 'flex', justifyContent: 'center', flexWrap: 'wrap', gap: 'var(--space-4)', marginTop: 'var(--space-8)' }}>
        <button className="btn btn--ghost" onClick={onNewReading}>
          New Consultation
        </button>
        {user && (
          <button
            className="btn btn--ghost"
            onClick={() => navigate('/history')}
          >
            View Archive
          </button>
        )}
      </div>
    </section>
  );
}
