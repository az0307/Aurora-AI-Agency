import { useApp } from './context/AppContext';
import { useKeyboard } from './hooks/useKeyboard';
import Header from './components/Header';
import SearchBar from './components/SearchBar';
import Hero from './components/Hero';
import Stats from './components/Stats';
import Board from './components/Board';
import Feed from './components/Feed';
import Ladder from './components/Ladder';
import Drawer from './components/Drawer';
import Toast from './components/Toast';
import NewJobModal from './components/NewJobModal';
import ConfirmModal from './components/ConfirmModal';
import LoginModal from './components/LoginModal';

export default function App() {
  useKeyboard();

  return (
    <>
      <Header />
      <SearchBar />
      <Hero />
      <Stats />
      <div className="main">
        <div>
          <Board />
        </div>
        <Feed />
      </div>
      <Ladder />
      <Drawer />
      <NewJobModal />
      <ConfirmModal />
      <LoginModal />
      <Toast />
    </>
  );
}
