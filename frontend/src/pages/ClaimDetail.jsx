import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../utils/api';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { toast } from 'sonner';
import { ArrowLeft, FileText, DollarSign, Calendar, AlertCircle } from 'lucide-react';

const ClaimDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [claim, setClaim] = useState(null);
  const [loading, setLoading] = useState(true);

  // for preview modal
  const [selectedFile, setSelectedFile] = useState(null);

  // convert backslashes to slashes (in case backend sends Windows-style paths)
  const normalizePath = (path) => (path ? path.replace(/\\/g, '/') : '');

  // detect file type from extension
  const getFileTypeFromPath = (path) => {
    if (!path) return 'other';
    const cleanPath = normalizePath(path);
    const ext = cleanPath.split('.').pop().toLowerCase();
    if (['jpg', 'jpeg', 'png', 'webp', 'gif'].includes(ext)) return 'image';
    if (ext === 'pdf') return 'pdf';
    return 'other';
  };

  // build URL to show in <img> / <iframe>
  // if your API already returns full URL, this just returns it
  const getFileUrl = (path) => {
  if (!path) return '';

  const cleanPath = normalizePath(path); // keeps / instead of \

  // if backend already sends full URL, just return it
  if (cleanPath.startsWith('http')) return cleanPath;

  // try to reuse axios baseURL
  const base = api?.defaults?.baseURL || '';

  // Example: base = "http://localhost:8000/api"
  // We want:  "http://localhost:8000"
  const root = base
    .replace(/\/+$/, '')   // remove trailing slash
    .replace(/\/api$/, ''); // remove "/api" if present

  return `${root}/${cleanPath.replace(/^\/+/, '')}`;
};


  useEffect(() => {
    fetchClaimDetail();
  }, [id]);

  const fetchClaimDetail = async () => {
    try {
      const response = await api.get(`/claims/${id}`);
      setClaim(response.data);
    } catch (error) {
      toast.error('Failed to fetch claim details');
      navigate('/dashboard');
    } finally {
      setLoading(false);
    }
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

  const getConfidenceClass = (score) => {
    if (score >= 70) return 'confidence-high';
    if (score >= 40) return 'confidence-medium';
    return 'confidence-low';
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div className="page-container" data-testid="claim-detail-page">
      <Button
        variant="ghost"
        onClick={() => navigate('/dashboard')}
        className="mb-4"
        data-testid="back-button"
      >
        <ArrowLeft size={20} />
        Back to Dashboard
      </Button>

      <div className="grid grid-cols-1" style={{ gap: '2rem' }}>
        {/* Header Card */}
        <Card className="p-6">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              <h1 style={{ fontSize: '2rem', fontWeight: '700', marginBottom: '0.5rem' }}>
                {claim.hospital_name}
              </h1>
              <p style={{ color: '#718096' }}>Claim ID: {claim.id}</p>
            </div>
            <span className={`status-badge ${getStatusClass(claim.status)}`} data-testid="claim-status">
              {claim.status}
            </span>
          </div>
        </Card>

        {/* Confidence Score */}
        {claim.confidence_score && (
          <Card className="p-6 text-center">
            <h3 style={{ fontSize: '1.1rem', color: '#718096', marginBottom: '1rem' }}>Confidence Score</h3>
            <div className={`confidence-score ${getConfidenceClass(claim.confidence_score)}`} data-testid="confidence-score">
              {claim.confidence_score.toFixed(1)}%
            </div>
            <p style={{ color: '#718096', marginTop: '1rem' }}>
              {claim.confidence_score >= 70 && 'High confidence - Most details match your documents'}
              {claim.confidence_score >= 40 && claim.confidence_score < 70 && 'Medium confidence - Some details need verification'}
              {claim.confidence_score < 40 && 'Low confidence - Multiple issues found in your claim'}
            </p>
          </Card>
        )}

        <div className="grid grid-cols-2" style={{ gap: '2rem' }}>
          {/* Claim Information */}
          <Card className="p-6">
            <h3 className="card-title">Claim Information</h3>
            <div style={{ display: 'grid', gap: '1rem' }}>
              <div>
                <p style={{ fontSize: '0.85rem', color: '#718096' }}>Insurance ID</p>
                <p style={{ fontWeight: '500' }}>{claim.insurance_id}</p>
              </div>
              <div>
                <p style={{ fontSize: '0.85rem', color: '#718096' }}>Aadhar Number</p>
                <p style={{ fontWeight: '500' }}>{claim.aadhar_no}</p>
              </div>
              <div>
                <p style={{ fontSize: '0.85rem', color: '#718096' }}>Date of Admission</p>
                <p style={{ fontWeight: '500' }}>
                  <Calendar size={16} style={{ display: 'inline', marginRight: '0.5rem' }} />
                  {new Date(claim.date_of_admission).toLocaleDateString()}
                </p>
              </div>
              <div>
                <p style={{ fontSize: '0.85rem', color: '#718096' }}>Disease Description</p>
                <p style={{ fontWeight: '500' }}>{claim.disease_description}</p>
              </div>
            </div>
          </Card>

          {/* Financial Information */}
          <Card className="p-6">
            <h3 className="card-title">Financial Details</h3>
            <div style={{ display: 'grid', gap: '1rem' }}>
              <div>
                <p style={{ fontSize: '0.85rem', color: '#718096' }}>Total Claim Amount</p>
                <p style={{ fontSize: '1.5rem', fontWeight: '700', color: '#667eea' }}>
                  <DollarSign size={20} style={{ display: 'inline' }} />
                  ₹ {claim.total_claim_amount?.toLocaleString()}
                </p>
              </div>
              {claim.reimbursement_amount !== null && claim.reimbursement_amount !== undefined && (
                <div>
                  <p style={{ fontSize: '0.85rem', color: '#718096' }}>Reimbursement Amount</p>
                  <p style={{ fontSize: '1.5rem', fontWeight: '700', color: '#10b981' }} data-testid="reimbursement-amount">
                    ₹ {claim.reimbursement_amount?.toLocaleString()}
                  </p>
                </div>
              )}
            </div>
          </Card>
        </div>

        {/* Expenses */}
        <Card className="p-6">
          <h3 className="card-title">Expense Breakdown</h3>
          <table style={{ width: '100%', marginTop: '1rem' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #e2e8f0' }}>
                <th style={{ textAlign: 'left', padding: '0.75rem', color: '#718096', fontWeight: '600' }}>Expense</th>
                <th style={{ textAlign: 'right', padding: '0.75rem', color: '#718096', fontWeight: '600' }}>Amount</th>
              </tr>
            </thead>
            <tbody>
              {claim.expenses?.map((expense, index) => (
                <tr key={index} style={{ borderBottom: '1px solid #f7fafc' }}>
                  <td style={{ padding: '0.75rem' }}>{expense.expense_name}</td>
                  <td style={{ padding: '0.75rem', textAlign: 'right', fontWeight: '600' }}>₹ {expense.amount?.toLocaleString()}</td>
                </tr>
              ))}
              <tr style={{ borderTop: '2px solid #e2e8f0', fontWeight: '700' }}>
                <td style={{ padding: '0.75rem' }}>Total</td>
                <td style={{ padding: '0.75rem', textAlign: 'right', color: '#667eea' }}>₹ {claim.total_claim_amount?.toLocaleString()}</td>
              </tr>
            </tbody>
          </table>
        </Card>

        {/* Files */}
        {/* Files */}
        <Card className="p-6">
          <h3 className="card-title">Uploaded Documents</h3>
          <div
            className="grid grid-cols-2"
            style={{ gap: '1rem', marginTop: '1rem' }}
          >
            {claim.files?.map((file, index) => {
              const fileName = normalizePath(file.file_path).split('/').pop();
              return (
                <button
                  key={index}
                  type="button"
                  onClick={() => setSelectedFile(file)}
                  className="file-item w-full text-left bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-xl px-3 py-3 transition flex items-center gap-2"
                  data-testid={`file-${file.file_type}-${index}`}
                >
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-200">
                    <FileText size={16} />
                  </div>
                  <div>
                    <p style={{ fontWeight: '500', fontSize: '0.9rem' }}>
                      {file.file_type.toUpperCase()}
                    </p>
                    <p
                      style={{ fontSize: '0.8rem', color: '#718096' }}
                      className="truncate max-w-[220px]"
                    >
                      {fileName}
                    </p>
                    <p
                      style={{
                        fontSize: '0.75rem',
                        color: '#4f46e5',
                        marginTop: '0.15rem',
                      }}
                    >
                      Click to view
                    </p>
                  </div>
                </button>
              );
            })}
          </div>
        </Card>

        {/* Issues Summary */}
        {claim.issues_summary && (
          <Card className="p-6" style={{ background: '#fffbeb', border: '1px solid #fbbf24' }}>
            <h3 className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <AlertCircle size={24} color="#f59e0b" />
              Analysis Summary
            </h3>
            <div style={{ marginTop: '1rem', whiteSpace: 'pre-wrap', color: '#78350f', lineHeight: '1.6' }} data-testid="issues-summary">
              {claim.issues_summary}
            </div>
          </Card>
        )}
        {/* File Preview Modal */}
{selectedFile && (
  <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/40">
    <div className="bg-white rounded-2xl shadow-xl max-w-3xl w-full mx-4 overflow-hidden">
      {/* header */}
      <div className="flex items-center justify-between px-4 py-3 border-b">
        <div>
          <p className="text-xs font-semibold text-slate-500">
            {selectedFile.file_type.toUpperCase()}
          </p>
          <p className="text-sm font-medium text-slate-800">
            {normalizePath(selectedFile.file_path).split('/').pop()}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <a
            href={getFileUrl(selectedFile.file_path)}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs px-3 py-1 rounded-full border border-blue-500 text-blue-600 hover:bg-blue-50"
          >
            Open in new tab
          </a>
          <button
            onClick={() => setSelectedFile(null)}
            className="text-xs px-3 py-1 rounded-full border border-slate-300 text-slate-600 hover:bg-slate-50"
          >
            Close
          </button>
        </div>
      </div>

      {/* content */}
      <div className="p-4 max-h-[70vh] overflow-auto flex justify-center">
        {getFileTypeFromPath(selectedFile.file_path) === 'image' && (
          <img
            src={getFileUrl(selectedFile.file_path)}
            alt={selectedFile.file_type}
            className="max-h-[65vh] object-contain"
          />
        )}

        {getFileTypeFromPath(selectedFile.file_path) === 'pdf' && (
          <iframe
            src={getFileUrl(selectedFile.file_path)}
            title={selectedFile.file_type}
            className="w-full h-[65vh]"
          />
        )}

        {getFileTypeFromPath(selectedFile.file_path) === 'other' && (
          <div className="text-sm text-slate-600 text-center">
            Preview not available.
            <br />
            Use &quot;Open in new tab&quot; to view or download the file.
          </div>
        )}
      </div>
    </div>
  </div>
)}

      </div>
    </div>
  );
};

export default ClaimDetail;
