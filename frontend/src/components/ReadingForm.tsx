import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { readingsApi, APIRequestError, type SpreadType, type ReadingRead } from '../api';
import { useAuth } from '../contexts/useAuth';

const SPREAD_OPTIONS: Array<{ value: SpreadType; name: string; count: string; description: string }> = [
  { value: 'single_card',  name: 'Single Card',  count: '1 card',  description: 'Immediate guidance for this moment' },
  { value: 'three_card',   name: 'Three Card',   count: '3 cards', description: 'Past · Present · Future' },
  { value: 'celtic_cross', name: 'Celtic Cross',  count: '10 cards',description: 'A complete consultation of the Fog' },
];

interface ReadingFormProps {
  onComplete: (reading: ReadingRead) => void;
}

export function ReadingForm({ onComplete }: ReadingFormProps) {
  const { user } = useAuth();
  const [spread, setSpread] = useState<SpreadType>('three_card');
  const [question, setQuestion] = useState('');

  const mutation = useMutation({
    mutationFn: () => readingsApi.create({ spread_type: spread, question: question.trim() || undefined }),
    onSuccess: onComplete,
  });

  const errorMessage = mutation.error instanceof APIRequestError
    ? mutation.error.body.error.message
    : mutation.error
    ? 'The Fog grows dense. Please try again.'
    : null;

  return (
    <form
      className="reading-panel"
      onSubmit={e => { e.preventDefault(); mutation.mutate(); }}
      aria-label="Initiate tarot reading"
    >
      <h2 className="reading-panel__title">Consult the Oracle</h2>
      <p className="reading-panel__subtitle">
        {user ? `Welcome, ${user.display_name}` : 'Guest consultation — sign in to preserve your archive'}
      </p>

      <div className="form-group">
        <p className="form-label" id="spread-label">Choose your Spread</p>
        <div className="spread-selector" role="radiogroup" aria-labelledby="spread-label">
          {SPREAD_OPTIONS.map(opt => (
            <button
              key={opt.value}
              type="button"
              role="radio"
              aria-checked={spread === opt.value}
              className={`spread-option${spread === opt.value ? ' spread-option--selected' : ''}`}
              onClick={() => setSpread(opt.value)}
            >
              <div className="spread-option__name">{opt.name}</div>
              <div className="spread-option__count">{opt.count}</div>
            </button>
          ))}
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="reading-question" className="form-label">
          Your question (optional)
        </label>
        <textarea
          id="reading-question"
          value={question}
          onChange={e => setQuestion(e.target.value)}
          maxLength={500}
          rows={3}
          placeholder="What does the Fog conceal from me?"
          style={{ resize: 'vertical' }}
          aria-describedby={errorMessage ? 'reading-error' : undefined}
        />
        <div style={{ textAlign: 'right', fontSize: 'var(--text-xs)', color: 'var(--color-ink-ghost)', marginTop: 'var(--space-1)' }}>
          {question.length}/500
        </div>
      </div>

      {errorMessage && (
        <div className="alert alert--error" id="reading-error" role="alert" aria-live="assertive">
          {errorMessage}
        </div>
      )}

      <button
        type="submit"
        className={`btn btn--primary btn--lg${mutation.isPending ? ' btn--loading' : ''}`}
        disabled={mutation.isPending}
        style={{ width: '100%', marginTop: 'var(--space-2)' }}
        aria-busy={mutation.isPending}
      >
        {mutation.isPending ? 'Drawing from the Fog' : 'Draw Cards'}
      </button>
    </form>
  );
}
