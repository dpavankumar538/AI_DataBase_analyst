/**
 * Helper functions for response extraction and safe parsing.
 */

export function getRouteLabel(route) {
  switch (route) {
    case 'structured':
      return { label: 'Structured SQL', color: 'blue' };
    case 'unstructured':
    case 'document':
      return { label: 'Document RAG', color: 'purple' };
    case 'hybrid':
      return { label: 'Hybrid Analysis', color: 'indigo' };
    case 'general':
      return { label: 'General AI', color: 'slate' };
    default:
      return { label: route || 'General', color: 'slate' };
  }
}

export function getStatusBadge(status) {
  const s = String(status || '').toLowerCase();
  if (s === 'completed' || s === 'connected' || s === 'success' || s === 'passed') {
    return { label: status, type: 'success' };
  }
  if (s === 'processing' || s === 'connecting' || s === 'retry') {
    return { label: status, type: 'warning' };
  }
  if (s === 'failed' || s === 'disconnected' || s === 'error') {
    return { label: status, type: 'error' };
  }
  return { label: status || 'Unknown', type: 'neutral' };
}
