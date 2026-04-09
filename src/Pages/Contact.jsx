import React, { useState } from 'react';
import Navbar from '../components/Navbar';
import { helpdeskAPI } from '../services/api';

export default function Contact() {
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [form, setForm] = useState({ name: '', email: '', message: '' });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!form.name.trim() || !form.email.trim() || !form.message.trim()) {
      setError('Please fill in all fields.');
      return;
    }

    setLoading(true);
    try {
      await helpdeskAPI.submitContact(form);
      setSent(true);
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : 'Failed to send message. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />
      <div className="max-w-3xl mx-auto p-6">
        <h1 className="text-2xl font-bold mb-4">Contact & Helpdesk</h1>
        <p className="text-slate-600 mb-6">
          For assistance, reach out to the helpdesk or use the grievance portal to lodge an issue.
        </p>

        {!sent ? (
          <form onSubmit={handleSubmit} className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
            {error && (
              <div className="mb-4 p-3 bg-red-50 border-l-4 border-red-500 rounded text-red-700 text-sm">
                ⚠️ {error}
              </div>
            )}
            <div className="grid grid-cols-1 gap-4">
              <input
                placeholder="Full name"
                value={form.name}
                onChange={e => setForm({ ...form, name: e.target.value })}
                className="p-3 border rounded"
                required
              />
              <input
                type="email"
                placeholder="Email"
                value={form.email}
                onChange={e => setForm({ ...form, email: e.target.value })}
                className="p-3 border rounded"
                required
              />
              <textarea
                placeholder="Message"
                value={form.message}
                onChange={e => setForm({ ...form, message: e.target.value })}
                className="p-3 border rounded h-32"
                required
              />
              <div className="flex justify-end">
                <button
                  type="submit"
                  disabled={loading}
                  className="bg-orange-600 hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed text-white px-6 py-2 rounded-md flex items-center gap-2 transition-all"
                >
                  {loading ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
                      Sending...
                    </>
                  ) : (
                    'Send'
                  )}
                </button>
              </div>
            </div>
          </form>
        ) : (
          <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100 text-center">
            <div className="text-4xl mb-3">✅</div>
            <h3 className="font-bold text-lg">Message Sent!</h3>
            <p className="text-slate-600 mt-2">Our helpdesk will contact you soon at <strong>{form.email}</strong>.</p>
            <button
              onClick={() => { setSent(false); setForm({ name: '', email: '', message: '' }); }}
              className="mt-4 text-blue-600 font-semibold hover:underline"
            >
              Send another
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
