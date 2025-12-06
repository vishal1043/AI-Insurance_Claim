import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../utils/api';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { toast } from 'sonner';
import { Shield, Plus, FileText, LogOut } from 'lucide-react';

const UserDashboard = () => {
  const navigate = useNavigate();
  const [claims, setClaims] = useState([]);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (!userData) {
      navigate('/login');
      return;
    }
    setUser(JSON.parse(userData));
    fetchClaims();
  }, [navigate]);

  const fetchClaims = async () => {
    try {
      const response = await api.get('/claims');
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
    navigate('/login');
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

  return (
    <div>
      <nav className="navbar">
        <div className="navbar-brand">
          <Shield size={32} />
          InsureClaim
        </div>
        <div className="navbar-menu">
          <span>Welcome, {user?.name}</span>
          <Button variant="ghost" onClick={handleLogout} data-testid="logout-button">
            <LogOut size={18} />
            Logout
          </Button>
        </div>
      </nav>

      <div className="page-container" data-testid="user-dashboard">
        <div className="dashboard-header">
          <h1 className="dashboard-title">My Claims Dashboard</h1>
          <p className="dashboard-subtitle">Manage and track your insurance claims</p>
          <Button
            onClick={() => navigate('/claims/new')}
            className="mt-4"
            data-testid="new-claim-button"
          >
            <Plus size={20} />
            Submit New Claim
          </Button>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '3rem' }}>
            <div className="spinner" style={{ margin: '0 auto' }}></div>
            <p style={{ marginTop: '1rem', color: '#718096' }}>Loading claims...</p>
          </div>
        ) : claims.length === 0 ? (
          <Card className="p-8 text-center" data-testid="no-claims-message">
            <FileText size={48} style={{ margin: '0 auto', color: '#cbd5e0' }} />
            <h3 style={{ marginTop: '1rem', color: '#4a5568' }}>No Claims Yet</h3>
            <p style={{ color: '#718096', marginTop: '0.5rem' }}>
              You haven't submitted any insurance claims. Click the button above to submit your first claim.
            </p>
          </Card>
        ) : (
          <div className="grid grid-cols-1" style={{ gap: '1.5rem' }}>
            {claims.map((claim) => (
              <Card
                key={claim.id}
                className="p-6 cursor-pointer"
                onClick={() => navigate(`/claims/${claim.id}`)}
                data-testid={`claim-card-${claim.id}`}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                  <div style={{ flex: 1 }}>
                    <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '0.5rem' }}>
                      {claim.hospital_name}
                    </h3>
                    <p style={{ color: '#718096', marginBottom: '1rem' }}>
                      Claim ID: {claim.id.substring(0, 8)}...
                    </p>
                    <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>
                      <div>
                        <p style={{ fontSize: '0.85rem', color: '#718096' }}>Date of Admission</p>
                        <p style={{ fontWeight: '500' }}>{new Date(claim.date_of_admission).toLocaleDateString()}</p>
                      </div>
                      <div>
                        <p style={{ fontSize: '0.85rem', color: '#718096' }}>Claim Amount</p>
                        <p style={{ fontWeight: '600', color: '#667eea' }}>₹ {claim.total_claim_amount?.toLocaleString()}</p>
                      </div>
                      {claim.confidence_score && (
                        <div>
                          <p style={{ fontSize: '0.85rem', color: '#718096' }}>Confidence Score</p>
                          <p style={{ fontWeight: '600' }}>{claim.confidence_score?.toFixed(1)}%</p>
                        </div>
                      )}
                      {claim.reimbursement_amount !== null && claim.reimbursement_amount !== undefined && (
                        <div>
                          <p style={{ fontSize: '0.85rem', color: '#718096' }}>Reimbursement</p>
                          <p style={{ fontWeight: '600', color: '#10b981' }}>₹ {claim.reimbursement_amount?.toLocaleString()}</p>
                        </div>
                      )}
                    </div>
                  </div>
                  <div>
                    <span className={`status-badge ${getStatusClass(claim.status)}`}>
                      {claim.status}
                    </span>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default UserDashboard;
