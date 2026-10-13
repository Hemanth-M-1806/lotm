import { useEffect } from 'react';
import type { ReadingCard as ReadingCardType } from '../api';

interface TarotCardProps {
  card: ReadingCardType;
  isFlipped?: boolean;
  onFlip?: () => void;
  /** Delay in ms before card auto-flips (for sequential reveal) */
  revealDelay?: number;
}

export function TarotCard({ card, isFlipped = true, onFlip, revealDelay }: TarotCardProps) {
  const orientation = card.is_reversed ? 'Reversed' : 'Upright';
  const cardName = card.card?.name ?? `Card ${card.card_id}`;
  const flipped = isFlipped;

  // Auto-flip after delay (for sequential reveal animations)
  useEffect(() => {
    if (revealDelay == null || flipped) return;
    const t = setTimeout(() => {
      onFlip?.();
    }, revealDelay);
    return () => clearTimeout(t);
  }, [revealDelay, flipped, onFlip]);

  const handleActivate = () => {
    if (!flipped) {
      onFlip?.();
    }
  };

  return (
    <div
      className={`tarot-card${flipped ? ' tarot-card--flipped' : ''}${card.is_reversed && flipped ? ' tarot-card--reversed' : ''}`}
      role="button"
      tabIndex={0}
      aria-label={flipped ? `${cardName}, ${orientation}` : 'Face-down tarot card — press Enter to reveal'}
      aria-pressed={flipped}
      onClick={handleActivate}
      onKeyDown={e => (e.key === 'Enter' || e.key === ' ') && handleActivate()}
    >
      <div className="tarot-card__inner">
        {/* Back face */}
        <div className="tarot-card__back" aria-hidden="true">
          <span className="tarot-card__back-sigil">✦</span>
        </div>

        {/* Front face */}
        <div className="tarot-card__face">
          <div className="tarot-card__art" aria-hidden="true">
            {card.card?.image_asset_path ? (
              <img
                src={card.card.image_asset_path}
                alt={`${cardName} tarot card illustration`}
                style={{ width: '100%', height: '100%', objectFit: 'cover' }}
              />
            ) : (
              <span className="tarot-card__art-placeholder" aria-label={`${cardName} — illustration pending`}>
                {cardName}
              </span>
            )}
          </div>
          <div className="tarot-card__name">{cardName}</div>
          <div className="tarot-card__orientation">{orientation}</div>
        </div>
      </div>
    </div>
  );
}
