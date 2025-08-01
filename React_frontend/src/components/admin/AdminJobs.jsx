import { Input } from '../ui/input'
import { Button } from '../ui/button';
import { useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import useGetJobByAdmin from '../hooks/useGetJobByAdmin';
import AdminJobsTable from './AdminJobsTable';
import { setSearchJobByText } from '@/redux/jobSlice';
import { useEffect, useState } from 'react';
import Header from '../shared/Header';
import Footer from '../shared/Footer';
import Chat from '../ai/Chat';
import { useTheme } from '@/context/ThemeContext';
import { Search, Plus } from 'lucide-react';

const AdminJobs = () => {
    
    const navigate = useNavigate();
    const dispatch = useDispatch();
    const { theme } = useTheme();
    useGetJobByAdmin();
    const [input, setInput] = useState("");

    useEffect(() => {
        dispatch(setSearchJobByText(input));
    }, [input, setInput])

    return (
        <div className="min-h-screen bg-background">
            <Header/>

            <div className='max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8'>
                <div className='flex flex-col space-y-6'>
                    {/* Header Section */}
                    <div className='flex flex-col space-y-2'>
                        <h1 className='text-3xl font-bold text-foreground'>Admin Jobs</h1>
                        <p className='text-muted-foreground'>Manage and monitor all job postings in one place</p>
                    </div>

                    {/* Search and Action Bar */}
                    <div className='flex flex-col sm:flex-row gap-4 items-center justify-between bg-card p-4 rounded-lg shadow-sm border border-border'>
                        <div className='relative w-full sm:w-[70%]'>
                            <Search className='absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground' />
                            <Input
                                type='text'
                                placeholder='Search jobs by title, company, or keywords...'
                                className='w-full pl-10 pr-4 py-2 bg-background text-foreground border-border focus:ring-2 focus:ring-primary/20 transition-all duration-200'
                                autoFocus={true}
                                required={true}
                                autoComplete='on'
                                spellCheck='false'
                                onChange={(e) => setInput(e.target.value)}
                            />
                        </div>
                        <Button
                            onClick={() => navigate('/admin/postJobs')}
                            className='w-full sm:w-auto flex items-center gap-2 bg-primary hover:bg-primary/90 text-primary-foreground transition-colors duration-200'
                        >
                            <Plus className='h-4 w-4' />
                            Post New Job
                        </Button>
                    </div>

                    {/* Jobs Table */}
                    <div className='bg-card rounded-lg shadow-sm border border-border overflow-hidden'>
                        <AdminJobsTable />
                    </div>
                </div>

                <Chat/>
            </div>
            <Footer/>
        </div>
    )
}

export default AdminJobs