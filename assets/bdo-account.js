// BestDealsOnline accounts + lead capture — Firebase (project bestdealsonline-us).
// Loaded as native ESM by /deal-check.html. All calls are safe to fail soft:
// the checker itself never depends on the network.

import { initializeApp } from 'https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js'
import {
  getAuth,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  sendPasswordResetEmail,
  signOut,
  onAuthStateChanged,
  updateProfile,
} from 'https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js'
import {
  getFirestore,
  doc,
  setDoc,
  getDoc,
  addDoc,
  collection,
  serverTimestamp,
  query,
  orderBy,
  limit,
  getDocs,
} from 'https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore.js'

const firebaseConfig = {
  apiKey: 'AIzaSyD6gn5jaoFcW1IzYhRNMzNgzxyCsG3tfzE',
  authDomain: 'bestdealsonline-us.firebaseapp.com',
  projectId: 'bestdealsonline-us',
  storageBucket: 'bestdealsonline-us.firebasestorage.app',
  messagingSenderId: '1056727354270',
  appId: '1:1056727354270:web:f22c79f65feada3eede48f',
}

const app = initializeApp(firebaseConfig)
const auth = getAuth(app)
const db = getFirestore(app)

export function watchAuth(callback) {
  return onAuthStateChanged(auth, callback)
}

export function currentUser() {
  return auth.currentUser
}

const FRIENDLY_ERRORS = {
  'auth/email-already-in-use': 'That email already has an account — try signing in instead.',
  'auth/invalid-email': "That doesn't look like an email address.",
  'auth/weak-password': 'Pick a password with at least 6 characters.',
  'auth/invalid-credential': "That email and password don't match.",
  'auth/wrong-password': "That email and password don't match.",
  'auth/user-not-found': "No account with that email yet — create one, it's free.",
  'auth/too-many-requests': 'Too many tries — wait a minute and try again.',
  'auth/network-request-failed': 'No connection — check your internet and try again.',
}

export function friendlyAuthError(err) {
  return FRIENDLY_ERRORS[err?.code] || 'Something went wrong — please try again.'
}

export async function signUp(email, password, firstName) {
  const cred = await createUserWithEmailAndPassword(auth, email.trim(), password)
  if (firstName) {
    await updateProfile(cred.user, { displayName: firstName.trim() }).catch(() => {})
  }
  await setDoc(
    doc(db, 'users', cred.user.uid),
    { firstName: firstName?.trim() || null, email: email.trim(), createdAt: serverTimestamp() },
    { merge: true }
  ).catch(() => {})
  return cred.user
}

export async function signIn(email, password) {
  const cred = await signInWithEmailAndPassword(auth, email.trim(), password)
  return cred.user
}

export function resetPassword(email) {
  return sendPasswordResetEmail(auth, email.trim())
}

export function logOut() {
  return signOut(auth)
}

// ---- Lead capture (works signed-out; rules allow create only) ----
export async function saveLead({ lookingFor, budget, email, source, asin, url }) {
  const data = { lookingFor: String(lookingFor || '').slice(0, 280), createdAt: serverTimestamp() }
  if (budget) data.budget = String(budget).slice(0, 30)
  if (email) data.email = String(email).slice(0, 110)
  if (source) data.source = String(source).slice(0, 50)
  if (asin) data.asin = String(asin).slice(0, 15)
  if (url) data.url = String(url).slice(0, 480)
  return addDoc(collection(db, 'leads'), data)
}

// ---- Per-user data ----
export async function saveCheck(user, check) {
  if (!user) return null
  return addDoc(collection(db, 'users', user.uid, 'checks'), {
    ...check,
    createdAt: serverTimestamp(),
  })
}

export async function loadRecentChecks(user, count = 10) {
  if (!user) return []
  const q = query(collection(db, 'users', user.uid, 'checks'), orderBy('createdAt', 'desc'), limit(count))
  const snap = await getDocs(q)
  return snap.docs.map((d) => ({ id: d.id, ...d.data() }))
}

export async function syncTally(user, tally) {
  if (!user) return
  await setDoc(doc(db, 'users', user.uid), { tally }, { merge: true }).catch(() => {})
}

export async function loadProfile(user) {
  if (!user) return null
  const snap = await getDoc(doc(db, 'users', user.uid)).catch(() => null)
  return snap && snap.exists() ? snap.data() : null
}
