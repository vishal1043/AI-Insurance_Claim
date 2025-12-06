import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../utils/api';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { toast } from 'sonner';
import { Shield, LogOut, FileText, AlertTriangle } from 'lucide-react';

const AdminDashboard = () => {
  const navigate = useNavigate();
  const [claims, setClaims] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    if (user.role !== 'admin') {
      navigate('/admin/login');
      return;
    }
    fetchClaims();
  }, [navigate]);

  const fetchClaims = async () => {
    try {
      const response = await api.get('/admin/claims');
      setClaims(response.data);
    } catch (error) {
      toast.error('Failed to fetch claims');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/admin/login');
  };

  const getStatusClass = (status) => {
    const statusMap = {
      'Submitted': 'status-submitted',
      'Under Review': 'status-under-review',
      'Approved': 'status-approved',
      'Rejected': 'status-rejected',
    };
    return statusMap[status] || 'status-under-review';
  };

  const hasIssues = (claim) => {
    return claim.confidence_score < 60 || (claim.issues_summary && claim.issues_summary.includes('⚠️'));
  };

  return (
    <div>
      <nav className="navbar">
        <div className="navbar-brand">
          <Shield size={32} />
          InsureClaim Admin
        </div>
        <div className="navbar-menu">
          <span>Admin Portal</span>
          <Button variant="ghost" onClick={handleLogout} data-testid="admin-logout-button">
            <LogOut size={18} />
            Logout
          </Button>
        </div>
      </nav>

      <div className="page-container" data-testid="admin-dashboard">
        <div className="dashboard-header">
          <h1 className="dashboard-title">Claims Management</h1>
          <p className="dashboard-subtitle">Review and process insurance claims</p>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '3rem' }}>
            <div className="spinner" style={{ margin: '0 auto' }}></div>
            <p style={{ marginTop: '1rem', color: '#718096' }}>Loading claims...</p>
          </div>
        ) : claims.length === 0 ? (
          <Card className="p-8 text-center" data-testid="no-claims-message">
            <FileText size={48} style={{ margin: '0 auto', color: '#cbd5e0' }} />
            <h3 style={{ marginTop: '1rem', color: '#4a5568' }}>No Claims Found</h3>
            <p style={{ color: '#718096', marginTop: '0.5rem' }}>There are no insurance claims to review.</p>
          </Card>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', background: 'white', borderRadius: '20px', overflow: 'hidden', boxShadow: '0 10px 40px rgba(0, 0, 0, 0.08)' }}>
              <thead style={{ background: '#f7fafc', borderBottom: '2px solid #e2e8f0' }}>
                <tr>
                  <th style={{ padding: '1rem', textAlign: 'left', fontWeight: '600', color: '#4a5568' }}>Claim ID</th>
                  <th style={{ padding: '1rem', textAlign: 'left', fontWeight: '600', color: '#4a5568' }}>Hospital</th>
                  <th style={{ padding: '1rem', textAlign: 'left', fontWeight: '600', color: '#4a5568' }}>Amount</th>
                  <th style={{ padding: '1rem', textAlign: 'left', fontWeight: '600', color: '#4a5568' }}>Confidence</th>
                  <th style={{ padding: '1rem', textAlign: 'left', fontWeight: '600', color: '#4a5568' }}>Status</th>
                  <th style={{ padding: '1rem', textAlign: 'center', fontWeight: '600', color: '#4a5568' }}>Alert</th>
                  <th style={{ padding: '1rem', textAlign: 'center', fontWeight: '600', color: '#4a5568' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {claims.map((claim) => (
                  <tr
                    key={claim.id}
                    style={{ borderBottom: '1px solid #f7fafc', transition: 'background 0.2s' }}
                    onMouseEnter={(e) => e.currentTarget.style.background = '#f7fafc'}
                    onMouseLeave={(e) => e.currentTarget.style.background = 'white'}
                    data-testid={`admin-claim-row-${claim.id}`}
                  >
                    <td style={{ padding: '1rem', fontFamily: 'monospace', fontSize: '0.9rem' }}>
                      {claim.id.substring(0, 8)}...
                    </td>
                    <td style={{ padding: '1rem', fontWeight: '500' }}>{claim.hospital_name}</td>
                    <td style={{ padding: '1rem', fontWeight: '600', color: '#667eea' }}>
                      ₹ {claim.total_claim_amount?.toLocaleString()}
                    </td>
                    <td style={{ padding: '1rem' }}>
                      {claim.confidence_score ? (
                        <span style={{ 
                          fontWeight: '600',
                          color: claim.confidence_score >= 70 ? '#10b981' : claim.confidence_score >= 40 ? '#f59e0b' : '#ef4444'
                        }}>
                          {claim.confidence_score.toFixed(1)}%
                        </span>
                      ) : '-'}
                    </td>
                    <td style={{ padding: '1rem' }}>
                      <span className={`status-badge ${getStatusClass(claim.status)}`}>
                        {claim.status}
                      </span>
                    </td>
                    <td style={{ padding: '1rem', textAlign: 'center' }}>
                      {hasIssues(claim) && (
                        <AlertTriangle size={20} color="#ef4444" data-testid={`alert-${claim.id}`} />
                      )}
                    </td>
                    <td style={{ padding: '1rem', textAlign: 'center' }}>
                      <Button
                        size="sm"
                        onClick={() => navigate(`/admin/claims/${claim.id}`)}
                        data-testid={`view-claim-${claim.id}`}
                      >
                        Review
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminDashboard;
