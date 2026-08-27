export function PageHeader({ title, subtitle, date }: { title: string; subtitle: string; date?: string }) {
  return (
    <div className="hero">
      <div>
        <div className="tag">{title}</div>
        <h1 className="title">{subtitle}</h1>
      </div>
      {date ? <div className="meta">{date}</div> : null}
    </div>
  );
}
