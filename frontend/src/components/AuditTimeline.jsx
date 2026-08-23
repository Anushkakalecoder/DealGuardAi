export default function AuditTimeline({ events }) {
  if (!events?.length) return <div className="empty">No audit events yet.</div>
  return <div className="timeline">
    {events.map(event => <div className="timeline-item" key={event.id}>
      <div className="timeline-dot" />
      <div className="timeline-content">
        <div className="timeline-head"><strong>{event.event_type.replaceAll('_',' ')}</strong><span>{new Date(event.created_at).toLocaleTimeString()}</span></div>
        <div className="muted tiny">Actor: {event.actor}</div>
        <pre>{JSON.stringify(event.details, null, 2)}</pre>
      </div>
    </div>)}
  </div>
}
