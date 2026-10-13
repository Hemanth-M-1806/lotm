import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { readingsApi, APIRequestError, type ReadingRead, type PaginatedResponse } from '../api';
import { useAuth } from '../contexts/useAuth';

const SPREAD_LABELS: Record<string, string> = {
  single_card:  'Single Card',
  three_card:   'Three Card',
  celtic_cross: 'Celtic Cross',
};

function formatDate(iso: string): string {
  return new Intl.DateTimeFormat(undefined, {
    year: 'numeric', month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit',
  }).format(new Date(iso));
}

export function HistoryPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['readings'],
    queryFn: () => readingsApi.list({ page: 1, page_size: 20 }),
    enabled: !!user,
  });

  const favMutation = useMutation({
    mutationFn: ({ id, is_favorite }: { id: string; is_favorite: boolean }) =>
      readingsApi.toggleFavorite(id, is_favorite),
    onSuccess: (updated: ReadingRead) => {
      queryClient.setQueryData<PaginatedResponse<ReadingRead>>(['readings'], (old) => {
        if (!old) return old;
        return {
          ...old,
          items: old.items.map((r: ReadingRead) => (r.id === updated.id ? updated : r)),
        };
      });
    },
  });

  if (!user) {
    return (
      <main style={{ minHeight: '100dvh', paddingTop: 'var(--space-24)', paddingBottom: 'var(--space-16)' }}>
        <div className="container">
          <div className="empty-state">
            <div className="empty-state__sigil" aria-hidden="true">✦</div>
            <h1 className="empty-state__title">Your archive awaits</h1>
            <p className="empty-state__body">
              Sign in to preserve and revisit your consultation history.
            </p>
            <button
              className="btn btn--primary"
              style={{ marginTop: 'var(--space-6)' }}
              onClick={() => navigate('/login')}
            >
              Sign in
            </button>
          </div>
        </div>
      </main>
    );
  }

  const errorMessage = isError
    ? (error instanceof APIRequestError ? error.body.error.message : 'Could not retrieve your archive.')
    : null;

  return (
    <main
      style={{ minHeight: '100dvh', paddingTop: 'var(--space-24)', paddingBottom: 'var(--space-16)' }}
      aria-label="Reading archive"
    >
      <div className="container">
        <header style={{ marginBottom: 'var(--space-8)' }}>
          <p
            className="font-ornament text-sm text-brass"
            style={{ letterSpacing: '0.2em', textTransform: 'uppercase', marginBottom: 'var(--space-2)' }}
          >
            Your Consultations
          </p>
          <h1 className="font-display text-3xl text-parchment italic">
            The Archive
          </h1>
          <div className="ornament-divider" style={{ marginTop: 'var(--space-4)' }} aria-hidden="true" />
        </header>

        {isLoading && (
          <div className="loading-ritual" role="status" aria-live="polite">
            <div className="loading-ritual__spinner" />
            <span>Consulting the Fog</span>
          </div>
        )}

        {errorMessage && (
          <div className="alert alert--error" role="alert">
            {errorMessage}
          </div>
        )}

        {!isLoading && data?.items.length === 0 && (
          <div className="empty-state">
            <div className="empty-state__sigil" aria-hidden="true">☾</div>
            <h2 className="empty-state__title">No consultations yet</h2>
            <p className="empty-state__body">
              The cards have not yet spoken to you. Return to the Oracle to begin your first reading.
            </p>
            <button
              className="btn btn--ghost"
              style={{ marginTop: 'var(--space-6)' }}
              onClick={() => navigate('/')}
            >
              Consult the Oracle
            </button>
          </div>
        )}

        {!isLoading && data && data.items.length > 0 && (
          <div
            style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}
            role="list"
            aria-label="Past readings"
          >
            {data.items.map(reading => {
              const isExpanded = expandedId === reading.id;
              return (
                <article
                  key={reading.id}
                  className={`history-card${isExpanded ? ' history-card--expanded' : ''}`}
                  role="listitem"
                >
                  {/* Card header row — always visible */}
                  <div className="history-card__header">
                    <button
                      className="history-card__expand-btn"
                      aria-expanded={isExpanded}
                      aria-controls={`reading-detail-${reading.id}`}
                      onClick={() => setExpandedId(isExpanded ? null : reading.id)}
                    >
                      <span className="history-card__spread">
                        {SPREAD_LABELS[reading.spread_type] ?? reading.spread_type}
                      </span>
                      <p className="history-card__question">
                        {reading.question ? `\u201c${reading.question}\u201d` : 'Silent consultation'}
                      </p>
                      <div className="history-card__cards-row" aria-label="Cards drawn">
                        {reading.cards.map(rc => (
                          <span key={rc.id} className="history-card__chip">
                            {rc.card?.name ?? `Card ${rc.card_id}`}
                            {rc.is_reversed ? ' \u2193' : ''}
                          </span>
                        ))}
                      </div>
                    </button>
                    <div style={{ display: 'flex', alignItems: 'flex-start', gap: 'var(--space-3)', flexShrink: 0 }}>
                      <span className="history-card__date">{formatDate(reading.created_at)}</span>
                      <button
                        className={`history-card__favorite-btn${reading.is_favorite ? ' history-card__favorite-btn--active' : ''}`}
                        aria-label={reading.is_favorite ? 'Remove from favourites' : 'Add to favourites'}
                        aria-pressed={reading.is_favorite}
                        onClick={e => {
                          e.stopPropagation();
                          favMutation.mutate({ id: reading.id, is_favorite: !reading.is_favorite });
                        }}
                      >
                        {reading.is_favorite ? '★' : '☆'}
                      </button>
                    </div>
                  </div>

                  {/* Expanded detail — interpretation */}
                  {isExpanded && (
                    <div
                      id={`reading-detail-${reading.id}`}
                      className="history-card__detail"
                      aria-label="Reading interpretation"
                    >
                      <div className="ornament-divider" style={{ margin: 'var(--space-4) 0' }} aria-hidden="true" />
                      {reading.interpretation ? (
                        <p className="interpretation__text" style={{ fontSize: 'var(--text-base)' }}>
                          {reading.interpretation}
                        </p>
                      ) : (
                        <p className="text-muted italic" style={{ fontSize: 'var(--text-sm)' }}>
                          No interpretation recorded for this consultation.
                        </p>
                      )}
                    </div>
                  )}
                </article>
              );
            })}
          </div>
        )}

        {data && data.total_pages > 1 && (
          <p style={{ textAlign: 'center', marginTop: 'var(--space-8)', color: 'var(--color-ink-ghost)', fontSize: 'var(--text-sm)' }}>
            Showing {data.items.length} of {data.total} consultations
          </p>
        )}
      </div>
    </main>
  );
}
