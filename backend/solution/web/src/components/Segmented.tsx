/** A row of toggle buttons (aria-pressed), as in the wireframe's range and view switches. */
export function Segmented<T extends string>({
  label,
  options,
  value,
  onChange,
}: {
  label: string;
  options: readonly T[];
  value: T;
  onChange: (value: T) => void;
}) {
  return (
    <div role="group" aria-label={label} className="inline-flex overflow-hidden rounded-lg border border-control">
      {options.map((option, i) => {
        const pressed = option === value;
        return (
          <button
            key={option}
            type="button"
            aria-pressed={pressed}
            onClick={() => onChange(option)}
            className={`min-h-9 cursor-pointer px-3.5 text-[13px] focus-visible:relative focus-visible:outline-2 focus-visible:outline-accent ${
              i > 0 ? 'border-l border-control' : ''
            } ${pressed ? 'bg-accent text-white' : 'bg-white text-ink hover:bg-ground'}`}
          >
            {option}
          </button>
        );
      })}
    </div>
  );
}
