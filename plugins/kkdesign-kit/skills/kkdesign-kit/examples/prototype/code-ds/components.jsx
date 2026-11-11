import { useId } from 'react';

export function Button({ children, className = '', type = 'button', ...props }) {
  return (
    <button className={`atlas-button atlas-button--primary${className ? ` ${className}` : ''}`} type={type} {...props}>
      {children}
    </button>
  );
}

export function TextField({ id, label, className = '', ...props }) {
  const generatedId = useId();
  const fieldId = id ?? generatedId;

  return (
    <div className={`atlas-field${className ? ` ${className}` : ''}`}>
      <label className="atlas-field__label" htmlFor={fieldId}>{label}</label>
      <input className="atlas-field__input" id={fieldId} {...props} />
    </div>
  );
}

export function Card({ children, className = '', ...props }) {
  return (
    <section className={`atlas-card${className ? ` ${className}` : ''}`} {...props}>
      {children}
    </section>
  );
}
