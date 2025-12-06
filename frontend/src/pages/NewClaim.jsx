import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../utils/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card } from '@/components/ui/card';
import { toast } from 'sonner';
import { ArrowLeft, Plus, X, Upload } from 'lucide-react';

const NewClaim = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    insurance_id: '',
    aadhar_no: '',
    hospital_name: '',
    date_of_admission: '',
    disease_description: '',
  });
  const [expenses, setExpenses] = useState([{ expense_name: '', amount: '' }]);
  const [bills, setBills] = useState([]);
  const [reports, setReports] = useState([]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleExpenseChange = (index, field, value) => {
    const newExpenses = [...expenses];
    newExpenses[index][field] = value;
    setExpenses(newExpenses);
  };

  const addExpense = () => {
    setExpenses([...expenses, { expense_name: '', amount: '' }]);
  };

  const removeExpense = (index) => {
    const newExpenses = expenses.filter((_, i) => i !== index);
    setExpenses(newExpenses);
  };

  const handleFileChange = (e, type) => {
    const files = Array.from(e.target.files);
    if (type === 'bills') {
      setBills([...bills, ...files]);
    } else {
      setReports([...reports, ...files]);
    }
  };

  const removeFile = (index, type) => {
    if (type === 'bills') {
      setBills(bills.filter((_, i) => i !== index));
    } else {
      setReports(reports.filter((_, i) => i !== index));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validation
    if (expenses.some(exp => !exp.expense_name || !exp.amount)) {
      toast.error('Please fill all expense details');
      return;
    }

    if (bills.length === 0) {
      toast.error('Please upload at least one bill');
      return;
    }

    setLoading(true);

    try {
      const formDataToSend = new FormData();
      
      // Prepare claim data
      const claimData = {
        ...formData,
        expenses: expenses.map(exp => ({
          expense_name: exp.expense_name,
          amount: parseFloat(exp.amount)
        }))
      };
      
      formDataToSend.append('claim_data', JSON.stringify(claimData));
      
      // Append files
      bills.forEach(file => {
        formDataToSend.append('bills', file);
      });
      
      reports.forEach(file => {
        formDataToSend.append('reports', file);
      });

      await api.post('/claims', formDataToSend, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      toast.success('Claim submitted successfully!');
      navigate('/dashboard');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to submit claim');
    } finally {
      setLoading(false);
    }
  };

  const totalAmount = expenses.reduce((sum, exp) => sum + (parseFloat(exp.amount) || 0), 0);

  return (
    <div className="page-container" data-testid="new-claim-page">
      <Button
        variant="ghost"
        onClick={() => navigate('/dashboard')}
        className="mb-4"
        data-testid="back-button"
      >
        <ArrowLeft size={20} />
        Back to Dashboard
      </Button>

      <Card className="p-8">
        <h1 style={{ fontSize: '2rem', fontWeight: '700', marginBottom: '2rem' }}>Submit New Claim</h1>

        <form onSubmit={handleSubmit}>
          <div className="grid grid-cols-2" style={{ gap: '1.5rem' }}>
            <div className="form-group">
              <Label htmlFor="name">Full Name</Label>
              <Input
                id="name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
                data-testid="name-input"
              />
            </div>

            <div className="form-group">
              <Label htmlFor="insurance_id">Insurance ID</Label>
              <Input
                id="insurance_id"
                name="insurance_id"
                value={formData.insurance_id}
                onChange={handleChange}
                required
                placeholder="POL001"
                data-testid="insurance-id-input"
              />
            </div>

            <div className="form-group">
              <Label htmlFor="aadhar_no">Aadhar Number</Label>
              <Input
                id="aadhar_no"
                name="aadhar_no"
                value={formData.aadhar_no}
                onChange={handleChange}
                required
                placeholder="1234 5678 9012"
                data-testid="aadhar-input"
              />
            </div>

            <div className="form-group">
              <Label htmlFor="hospital_name">Hospital Name</Label>
              <Input
                id="hospital_name"
                name="hospital_name"
                value={formData.hospital_name}
                onChange={handleChange}
                required
                data-testid="hospital-input"
              />
            </div>

            <div className="form-group">
              <Label htmlFor="date_of_admission">Date of Admission</Label>
              <Input
                id="date_of_admission"
                name="date_of_admission"
                type="date"
                value={formData.date_of_admission}
                onChange={handleChange}
                required
                data-testid="admission-date-input"
              />
            </div>
          </div>

          <div className="form-group">
            <Label htmlFor="disease_description">Disease Description</Label>
            <Textarea
              id="disease_description"
              name="disease_description"
              value={formData.disease_description}
              onChange={handleChange}
              required
              rows={4}
              placeholder="Describe the medical condition and treatment..."
              data-testid="disease-input"
            />
          </div>

          {/* Expenses */}
          <div style={{ marginTop: '2rem' }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>Expense Details</h3>
            {expenses.map((expense, index) => (
              <div key={index} style={{ display: 'flex', gap: '1rem', marginBottom: '1rem', alignItems: 'end' }}>
                <div style={{ flex: 1 }}>
                  <Label>Expense Name</Label>
                  <Input
                    value={expense.expense_name}
                    onChange={(e) => handleExpenseChange(index, 'expense_name', e.target.value)}
                    placeholder="e.g., Consultation Fee"
                    required
                    data-testid={`expense-name-${index}`}
                  />
                </div>
                <div style={{ width: '200px' }}>
                  <Label>Amount (₹)</Label>
                  <Input
                    type="number"
                    value={expense.amount}
                    onChange={(e) => handleExpenseChange(index, 'amount', e.target.value)}
                    placeholder="0.00"
                    required
                    data-testid={`expense-amount-${index}`}
                  />
                </div>
                {expenses.length > 1 && (
                  <Button
                    type="button"
                    variant="destructive"
                    onClick={() => removeExpense(index)}
                    data-testid={`remove-expense-${index}`}
                  >
                    <X size={20} />
                  </Button>
                )}
              </div>
            ))}
            <Button
              type="button"
              variant="outline"
              onClick={addExpense}
              data-testid="add-expense-button"
            >
              <Plus size={20} />
              Add Expense
            </Button>
            <div style={{ marginTop: '1rem', fontSize: '1.25rem', fontWeight: '600' }}>
              Total Claim Amount: <span style={{ color: '#667eea' }}>₹ {totalAmount.toLocaleString()}</span>
            </div>
          </div>

          {/* File Uploads */}
          <div style={{ marginTop: '2rem' }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>Upload Documents</h3>
            
            <div className="grid grid-cols-2" style={{ gap: '1.5rem' }}>
              <div>
                <Label>Bills (Required)</Label>
                <div className="file-upload-area" style={{ marginTop: '0.5rem' }}>
                  <input
                    type="file"
                    accept="image/*,.pdf"
                    multiple
                    onChange={(e) => handleFileChange(e, 'bills')}
                    style={{ display: 'none' }}
                    id="bills-upload"
                    data-testid="bills-upload"
                  />
                  <label htmlFor="bills-upload" style={{ cursor: 'pointer' }}>
                    <Upload size={32} style={{ margin: '0 auto', color: '#cbd5e0' }} />
                    <p style={{ marginTop: '0.5rem', color: '#718096' }}>Click to upload bills</p>
                  </label>
                </div>
                <div className="file-list">
                  {bills.map((file, index) => (
                    <div key={index} className="file-item" data-testid={`bill-file-${index}`}>
                      <span>{file.name}</span>
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => removeFile(index, 'bills')}
                      >
                        <X size={16} />
                      </Button>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <Label>Medical Reports (Optional)</Label>
                <div className="file-upload-area" style={{ marginTop: '0.5rem' }}>
                  <input
                    type="file"
                    accept="image/*,.pdf"
                    multiple
                    onChange={(e) => handleFileChange(e, 'reports')}
                    style={{ display: 'none' }}
                    id="reports-upload"
                    data-testid="reports-upload"
                  />
                  <label htmlFor="reports-upload" style={{ cursor: 'pointer' }}>
                    <Upload size={32} style={{ margin: '0 auto', color: '#cbd5e0' }} />
                    <p style={{ marginTop: '0.5rem', color: '#718096' }}>Click to upload reports</p>
                  </label>
                </div>
                <div className="file-list">
                  {reports.map((file, index) => (
                    <div key={index} className="file-item" data-testid={`report-file-${index}`}>
                      <span>{file.name}</span>
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => removeFile(index, 'reports')}
                      >
                        <X size={16} />
                      </Button>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <Button
            type="submit"
            disabled={loading}
            className="w-full mt-8"
            size="lg"
            data-testid="submit-claim-button"
          >
            {loading ? 'Submitting Claim...' : 'Submit Claim'}
          </Button>
        </form>
      </Card>
    </div>
  );
};

export default NewClaim;
