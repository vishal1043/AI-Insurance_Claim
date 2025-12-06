import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../utils/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card } from '@/components/ui/card';
import { toast } from 'sonner';
import {
  ArrowLeft,
  CheckCircle,
  XCircle,
  AlertCircle,
  User,
  FileText,
} from 'lucide-react';

const AdminClaimReview = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [claim, setClaim] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [reimbursementAmount, setReimbursementAmount] = useState('');
  const [remarks, setRemarks] = useState('');

  // 👇 NEW: for document preview modal
  const [selectedFile, setSelectedFile] = useState(null);

  // 👇 NEW: helpers for file preview
  const normalizePath = (path) =>
    path
      ? path
          .replace(/\\/g, '/') // Windows ➜ web
          .replace(/^backend\//, '') // in case old paths start with "backend/"
      : '';

  const getFileTypeFromPath = (path) => {
    if (!path) return 'other';
    const cleanPath = normalizePath(path);
    const ext = cleanPath.split('.').pop().toLowerCase();
    if (['jpg', 'jpeg', 'png', 'webp', 'gif'].includes(ext)) return 'image';
    if (ext === 'pdf') return 'pdf';
    return 'other';
  };

  const getFileUrl = (path) => {
    if (!path) return '';

    const cleanPath = normalizePath(path); // e.g. "uploads/reports/xyz.jpg"

    // If backend already returns full URL
    if (cleanPath.startsWith('http')) return cleanPath;

    // baseURL of axios, e.g. "http://localhost:8000" or "http://localhost:8000/api"
    const base = api?.defaults?.baseURL || '';

    // remove trailing slash and "/api" or "/api/v1" etc.
    const root = base
      .replace(/\/+$/, '')
      .replace(/\/api.*$/, ''); // "http://localhost:8000"

    // If DB path already starts with "uploads/..."
    if (cleanPath.startsWith('uploads/')) {
      return `${root}/${cleanPath}`;
    }

    // otherwise, prefix with uploads
    return `${root}/uploads/${cleanPath.replace(/^\/+/, '')}`;
  };

  useEffect(() => {
    fetchClaimDetail();
  }, [id]);

  const fetchClaimDetail = async () => {
    try {
      const response = await api.get(`/admin/claims/${id}`);
      setClaim(response.data);
      setReimbursementAmount(response.data.reimbursement_amount || '');
    } catch (error) {
      toast.error('Failed to fetch claim details');
      navigate('/admin/dashboard');
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (status) => {
    if (!reimbursementAmount) {
      toast.error('Please enter reimbursement amount');
      return;
    }

    setActionLoading(true);
    try {
      await api.put(`/admin/claims/${id}/action`, {
        status,
        reimbursement_amount: parseFloat(reimbursementAmount),
        remarks: remarks || null,
      });

      toast.success(`Claim ${status.toLowerCase()} successfully!`);
      navigate('/admin/dashboard');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Action failed');
    } finally {
      setActionLoading(false);
    }
  };

  const getConfidenceClass = (score) => {
    if (score >= 70) return 'confidence-high';
    if (score >= 40) return 'confidence-medium';
    return 'confidence-low';
  };

  if (loading) {
    return (
      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '100vh',
        }}
      >
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div
      className="page-container"
      data-testid="admin-claim-review-page"
    >
      <Button
        variant="ghost"
        onClick={() => navigate('/admin/dashboard')}
        className="mb-4"
        data-testid="back-to-admin-dashboard"
      >
        <ArrowLeft size={20} />
        Back to Dashboard
      </Button>

      <div
        className="grid grid-cols-1"
        style={{ gap: '2rem' }}
      >
        {/* Header */}
        <Card className="p-6">
          <h1
            style={{
              fontSize: '2rem',
              fontWeight: '700',
              marginBottom: '1rem',
            }}
          >
            Claim Review
          </h1>
          <p style={{ color: '#718096' }}>Claim ID: {claim.id}</p>
        </Card>

        {/* User Information */}
        {claim.user_info && (
          <Card className="p-6">
            <h3
              className="card-title"
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
              }}
            >
              <User size={24} />
              User Information
            </h3>
            <div
              className="grid grid-cols-2"
              style={{ gap: '1.5rem', marginTop: '1rem' }}
            >
              <div>
                <p style={{ fontSize: '0.85rem', color: '#718096' }}>
                  Name
                </p>
                <p style={{ fontWeight: '500' }}>
                  {claim.user_info.name}
                </p>
              </div>
              <div>
                <p style={{ fontSize: '0.85rem', color: '#718096' }}>
                  Email
                </p>
                <p style={{ fontWeight: '500' }}>
                  {claim.user_info.email}
                </p>
              </div>
              <div>
                <p style={{ fontSize: '0.85rem', color: '#718096' }}>
                  Mobile
                </p>
                <p style={{ fontWeight: '500' }}>
                  {claim.user_info.mobile_no}
                </p>
              </div>
              <div>
                <p style={{ fontSize: '0.85rem', color: '#718096' }}>
                  Date of Birth
                </p>
                <p style={{ fontWeight: '500' }}>
                  {new Date(
                    claim.user_info.dob
                  ).toLocaleDateString()}
                </p>
              </div>
            </div>
          </Card>
        )}

        {/* Insurance Policy Information */}
        {claim.policy_info && (
          <Card className="p-6">
            <h3 className="card-title">
              Insurance Policy Information
            </h3>
            <div
              className="grid grid-cols-2"
              style={{ gap: '1.5rem', marginTop: '1rem' }}
            >
              <div>
                <p style={{ fontSize: '0.85rem', color: '#718096' }}>
                  Insurance ID
                </p>
                <p style={{ fontWeight: '500' }}>
                  {claim.policy_info.insurance_id}
                </p>
              </div>
              <div>
                <p style={{ fontSize: '0.85rem', color: '#718096' }}>
                  Total Coverage
                </p>
                <p
                  style={{
                    fontWeight: '600',
                    color: '#667eea',
                  }}
                >
                  ₹{' '}
                  {claim.policy_info.total_coverage_amount?.toLocaleString()}
                </p>
              </div>
              <div>
                <p style={{ fontSize: '0.85rem', color: '#718096' }}>
                  Remaining Amount
                </p>
                <p
                  style={{
                    fontWeight: '600',
                    color: '#10b981',
                  }}
                >
                  ₹{' '}
                  {claim.policy_info.remaining_amount?.toLocaleString()}
                </p>
              </div>
              <div>
                <p style={{ fontSize: '0.85rem', color: '#718096' }}>
                  Expiry Date
                </p>
                <p style={{ fontWeight: '500' }}>
                  {new Date(
                    claim.policy_info.expiry_date
                  ).toLocaleDateString()}
                </p>
              </div>
              <div>
                <p style={{ fontSize: '0.85rem', color: '#718096' }}>
                  EMI Pending
                </p>
                <p
                  style={{
                    fontWeight: '500',
                    color: claim.policy_info.emi_pending
                      ? '#ef4444'
                      : '#10b981',
                  }}
                >
                  {claim.policy_info.emi_pending
                    ? 'Yes'
                    : 'No'}
                </p>
              </div>
              <div>
                <p style={{ fontSize: '0.85rem', color: '#718096' }}>
                  Policy Status
                </p>
                <p style={{ fontWeight: '500' }}>
                  {claim.policy_info.status.toUpperCase()}
                </p>
              </div>
            </div>
          </Card>
        )}

        {/* Confidence Score */}
        <Card className="p-6 text-center">
          <h3
            style={{
              fontSize: '1.1rem',
              color: '#718096',
              marginBottom: '1rem',
            }}
          >
            AI Confidence Score
          </h3>
          <div
            className={`confidence-score ${getConfidenceClass(
              claim.confidence_score
            )}`}
            data-testid="admin-confidence-score"
          >
            {claim.confidence_score?.toFixed(1)}%
          </div>
        </Card>

        {/* Claim Details */}
        <div
          className="grid grid-cols-2"
          style={{ gap: '2rem' }}
        >
          <Card className="p-6">
            <h3 className="card-title">Claim Information</h3>
            <div
              style={{
                display: 'grid',
                gap: '1rem',
                marginTop: '1rem',
              }}
            >
              <div>
                <p style={{ fontSize: '0.85rem', color: '#718096' }}>
                  Hospital Name
                </p>
                <p style={{ fontWeight: '500' }}>
                  {claim.hospital_name}
                </p>
              </div>
              <div>
                <p style={{ fontSize: '0.85rem', color: '#718096' }}>
                  Aadhar Number
                </p>
                <p style={{ fontWeight: '500' }}>
                  {claim.aadhar_no}
                </p>
              </div>
              <div>
                <p style={{ fontSize: '0.85rem', color: '#718096' }}>
                  Date of Admission
                </p>
                <p style={{ fontWeight: '500' }}>
                  {new Date(
                    claim.date_of_admission
                  ).toLocaleDateString()}
                </p>
              </div>
              <div>
                <p style={{ fontSize: '0.85rem', color: '#718096' }}>
                  Disease Description
                </p>
                <p style={{ fontWeight: '500' }}>
                  {claim.disease_description}
                </p>
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <h3 className="card-title">Financial Summary</h3>
            <div
              style={{
                display: 'grid',
                gap: '1rem',
                marginTop: '1rem',
              }}
            >
              <div>
                <p style={{ fontSize: '0.85rem', color: '#718096' }}>
                  Total Claim Amount
                </p>
                <p
                  style={{
                    fontSize: '1.5rem',
                    fontWeight: '700',
                    color: '#667eea',
                  }}
                >
                  ₹ {claim.total_claim_amount?.toLocaleString()}
                </p>
              </div>
              <div>
                <p style={{ fontSize: '0.85rem', color: '#718096' }}>
                  Current Status
                </p>
                <p style={{ fontWeight: '600' }}>{claim.status}</p>
              </div>
            </div>
          </Card>
        </div>

        {/* Expenses */}
        <Card className="p-6">
          <h3 className="card-title">Expense Breakdown</h3>
          <table
            style={{ width: '100%', marginTop: '1rem' }}
          >
            <thead>
              <tr style={{ borderBottom: '2px solid #e2e8f0' }}>
                <th
                  style={{
                    textAlign: 'left',
                    padding: '0.75rem',
                    color: '#718096',
                    fontWeight: '600',
                  }}
                >
                  Expense
                </th>
                <th
                  style={{
                    textAlign: 'right',
                    padding: '0.75rem',
                    color: '#718096',
                    fontWeight: '600',
                  }}
                >
                  Amount
                </th>
              </tr>
            </thead>
            <tbody>
              {claim.expenses?.map((expense, index) => (
                <tr
                  key={index}
                  style={{ borderBottom: '1px solid #f7fafc' }}
                >
                  <td style={{ padding: '0.75rem' }}>
                    {expense.expense_name}
                  </td>
                  <td
                    style={{
                      padding: '0.75rem',
                      textAlign: 'right',
                      fontWeight: '600',
                    }}
                  >
                    ₹ {expense.amount?.toLocaleString()}
                  </td>
                </tr>
              ))}
              <tr
                style={{
                  borderTop: '2px solid #e2e8f0',
                  fontWeight: '700',
                }}
              >
                <td style={{ padding: '0.75rem' }}>Total</td>
                <td
                  style={{
                    padding: '0.75rem',
                    textAlign: 'right',
                    color: '#667eea',
                  }}
                >
                  ₹ {claim.total_claim_amount?.toLocaleString()}
                </td>
              </tr>
            </tbody>
          </table>
        </Card>

        {/* Documents – UPDATED WITH PREVIEW */}
        <Card className="p-6">
          <h3 className="card-title">Uploaded Documents</h3>
          <div style={{ marginTop: '1rem' }}>
            {claim.files?.map((file, index) => {
              const fileName = normalizePath(
                file.file_path
              ).split('/').pop();
              return (
                <div
                  key={index}
                  style={{ marginBottom: '2rem' }}
                >
                  {/* Clickable header row */}
                  <button
                    type="button"
                    onClick={() => setSelectedFile(file)}
                    className="w-full text-left bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-xl px-3 py-3 transition flex items-center gap-2"
                  >
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-200">
                      <FileText size={16} />
                    </div>
                    <div>
                      <p
                        style={{
                          fontWeight: '600',
                          fontSize: '0.9rem',
                        }}
                      >
                        {file.file_type.toUpperCase()} : {fileName}
                      </p>
                      <p
                        style={{
                          fontSize: '0.75rem',
                          color: '#4f46e5',
                          marginTop: '0.15rem',
                        }}
                      >
                        Click to view document
                      </p>
                    </div>
                  </button>

                  {/* Extracted text (same as before) */}
                  {file.extracted_text && (
                    <div
                      style={{
                        background: '#f7fafc',
                        padding: '1rem',
                        borderRadius: '8px',
                        maxHeight: '200px',
                        overflowY: 'auto',
                        fontSize: '0.85rem',
                        whiteSpace: 'pre-wrap',
                        fontFamily: 'monospace',
                        marginTop: '0.75rem',
                      }}
                      data-testid={`extracted-text-${index}`}
                    >
                      {file.extracted_text || 'No text extracted'}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </Card>

        {/* AI Analysis & Issues */}
        {claim.issues_summary && (
          <Card
            className="p-6"
            style={{
              background: '#fef3c7',
              border: '2px solid #f59e0b',
            }}
          >
            <h3
              className="card-title"
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
              }}
            >
              <AlertCircle size={24} color="#f59e0b" />
              Analysis & Issues Found
            </h3>
            <div
              style={{
                marginTop: '1rem',
                whiteSpace: 'pre-wrap',
                color: '#78350f',
                lineHeight: '1.8',
              }}
              data-testid="admin-issues-summary"
            >
              {claim.issues_summary}
            </div>
          </Card>
        )}

        {/* Admin Action */}
        {claim.status !== 'Approved' &&
          claim.status !== 'Rejected' && (
            <Card
              className="p-6"
              style={{
                background: '#f0fdf4',
                border: '2px solid #10b981',
              }}
            >
              <h3 className="card-title">Admin Action</h3>
              <div style={{ marginTop: '1rem' }}>
                <div className="form-group">
                  <Label htmlFor="reimbursement">
                    Final Reimbursement Amount (₹)
                  </Label>
                  <Input
                    id="reimbursement"
                    type="number"
                    value={reimbursementAmount}
                    onChange={(e) =>
                      setReimbursementAmount(e.target.value)
                    }
                    placeholder="Enter reimbursement amount"
                    data-testid="reimbursement-input"
                  />
                </div>

                <div className="form-group">
                  <Label htmlFor="remarks">
                    Remarks (Optional)
                  </Label>
                  <Textarea
                    id="remarks"
                    value={remarks}
                    onChange={(e) =>
                      setRemarks(e.target.value)
                    }
                    placeholder="Add any additional comments or reasons..."
                    rows={3}
                    data-testid="remarks-input"
                  />
                </div>

                <div
                  style={{
                    display: 'flex',
                    gap: '1rem',
                    marginTop: '1.5rem',
                  }}
                >
                  <Button
                    onClick={() => handleAction('Approved')}
                    disabled={actionLoading}
                    style={{
                      flex: 1,
                      background: '#10b981',
                    }}
                    data-testid="approve-button"
                  >
                    <CheckCircle size={20} />
                    {actionLoading
                      ? 'Processing...'
                      : 'Approve Claim'}
                  </Button>
                  <Button
                    onClick={() => handleAction('Rejected')}
                    disabled={actionLoading}
                    variant="destructive"
                    style={{ flex: 1 }}
                    data-testid="reject-button"
                  >
                    <XCircle size={20} />
                    {actionLoading
                      ? 'Processing...'
                      : 'Reject Claim'}
                  </Button>
                </div>
              </div>
            </Card>
          )}

        {(claim.status === 'Approved' ||
          claim.status === 'Rejected') && (
          <Card
            className="p-6 text-center"
            style={{
              background:
                claim.status === 'Approved'
                  ? '#d1fae5'
                  : '#fee2e2',
            }}
          >
            <h3
              style={{
                fontSize: '1.5rem',
                fontWeight: '600',
                color:
                  claim.status === 'Approved'
                    ? '#065f46'
                    : '#991b1b',
              }}
            >
              This claim has been{' '}
              {claim.status.toLowerCase()}
            </h3>
          </Card>
        )}
      </div>

      {/* 👇 File Preview Modal (same logic as user side) */}
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
                  {normalizePath(
                    selectedFile.file_path
                  ).split('/').pop()}
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
              {getFileTypeFromPath(
                selectedFile.file_path
              ) === 'image' && (
                <img
                  src={getFileUrl(selectedFile.file_path)}
                  alt={selectedFile.file_type}
                  className="max-h-[65vh] object-contain"
                />
              )}

              {getFileTypeFromPath(
                selectedFile.file_path
              ) === 'pdf' && (
                <iframe
                  src={getFileUrl(selectedFile.file_path)}
                  title={selectedFile.file_type}
                  className="w-full h-[65vh]"
                />
              )}

              {getFileTypeFromPath(
                selectedFile.file_path
              ) === 'other' && (
                <div className="text-sm text-slate-600 text-center">
                  Preview not available.
                  <br />
                  Use &quot;Open in new tab&quot; to view or
                  download the file.
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminClaimReview;
